from __future__ import annotations

from typing import Any

import numpy as np

from app.modules.omr_reader.bubble_classifier import classify_bubbles
from app.modules.omr_reader.contracts import BubbleReadResult


def read_auxiliary_blocks(
    *,
    aligned_image: np.ndarray,
    metadata: dict[str, Any],
    px_per_mm: float,
    marked_threshold: float,
    unmarked_threshold: float,
    robust_mode: bool,
) -> dict[str, Any]:
    blocks = metadata.get("auxiliary_blocks", [])
    if not isinstance(blocks, list) or len(blocks) == 0:
        return {"blocks": [], "summary": {"total_blocks": 0, "manual_review_blocks": 0}}

    payload_blocks: list[dict[str, Any]] = []
    manual_review_blocks = 0

    for block in blocks:
        if not isinstance(block, dict):
            continue
        if str(block.get("block_type", "")) != "omr":
            continue
        omr_cfg = block.get("omr_config")
        if not isinstance(omr_cfg, dict):
            continue

        synthetic_metadata = {
            "bubbles": _build_block_bubbles(block=block, omr_config=omr_cfg),
        }
        bubble_results = classify_bubbles(
            aligned_image=aligned_image,
            metadata=synthetic_metadata,
            px_per_mm=px_per_mm,
            marked_threshold=marked_threshold,
            unmarked_threshold=unmarked_threshold,
            robust_mode=robust_mode,
        )
        block_payload = _build_block_payload(
            block=block,
            omr_config=omr_cfg,
            bubble_results=bubble_results,
        )
        payload_blocks.append(block_payload)
        if block_payload.get("manual_review_required"):
            manual_review_blocks += 1

    return {
        "blocks": payload_blocks,
        "summary": {
            "total_blocks": len(payload_blocks),
            "manual_review_blocks": manual_review_blocks,
        },
    }


def _build_block_bubbles(*, block: dict[str, Any], omr_config: dict[str, Any]) -> list[dict[str, Any]]:
    block_id = str(block.get("block_id", "aux"))
    x_mm = float(block["x_mm"])
    y_mm = float(block["y_mm"])
    width_mm = float(block["width_mm"])
    height_mm = float(block["height_mm"])

    rows = int(omr_config["rows"])
    cols = int(omr_config["cols"])
    diameter_mm = float(omr_config["bubble_diameter_mm"])
    radius_mm = diameter_mm / 2.0
    spacing_x_mm = float(omr_config["spacing_x_mm"])
    spacing_y_mm = float(omr_config["spacing_y_mm"])

    grid_width_mm = diameter_mm + (cols - 1) * spacing_x_mm
    grid_height_mm = diameter_mm + (rows - 1) * spacing_y_mm

    left_padding_mm = omr_config.get("left_padding_mm")
    top_padding_mm = omr_config.get("top_padding_mm")

    if left_padding_mm is None:
        origin_x_mm = x_mm + (width_mm - grid_width_mm) / 2.0
    else:
        origin_x_mm = x_mm + float(left_padding_mm)

    if top_padding_mm is None:
        origin_y_mm = y_mm + (height_mm - grid_height_mm) / 2.0
    else:
        origin_y_mm = y_mm + float(top_padding_mm)

    row_labels = omr_config.get("row_labels")
    col_labels = omr_config.get("col_labels")

    bubbles: list[dict[str, Any]] = []
    for row in range(rows):
        for col in range(cols):
            cx_mm = origin_x_mm + radius_mm + col * spacing_x_mm
            cy_mm = origin_y_mm + radius_mm + row * spacing_y_mm
            label = _resolve_cell_label(
                row=row,
                col=col,
                row_labels=row_labels,
                col_labels=col_labels,
            )
            bubbles.append(
                {
                    "bubble_id": f"{block_id}_{row:02d}_{col:02d}",
                    "group_id": block_id,
                    "row": row,
                    "col": col,
                    "label": label,
                    "center_x_mm": cx_mm,
                    "center_y_mm": cy_mm,
                    "radius_mm": radius_mm,
                }
            )
    return bubbles


def _resolve_cell_label(
    *,
    row: int,
    col: int,
    row_labels: Any,
    col_labels: Any,
) -> str:
    if isinstance(col_labels, list) and col < len(col_labels):
        return str(col_labels[col])
    if isinstance(row_labels, list) and row < len(row_labels):
        return str(row_labels[row])
    return f"r{row}c{col}"


def _build_block_payload(
    *,
    block: dict[str, Any],
    omr_config: dict[str, Any],
    bubble_results: list[BubbleReadResult],
) -> dict[str, Any]:
    rows = int(omr_config["rows"])
    cols = int(omr_config["cols"])
    selection_mode = str(omr_config.get("selection_mode", "single_per_column"))
    row_labels = omr_config.get("row_labels")

    by_col: dict[int, list[BubbleReadResult]] = {}
    for item in bubble_results:
        by_col.setdefault(item.col, []).append(item)
    for col in by_col:
        by_col[col].sort(key=lambda item: item.row)

    column_results: list[dict[str, Any]] = []
    manual_review_required = False

    if selection_mode == "single_choice":
        selected_row, marked_rows, ambiguous_rows = _select_single_choice(
            bubble_results=bubble_results
        )
        ratios = {
            item.row: round(float(item.fill_ratio), 6)
            for item in bubble_results
        }
        value = _label_for_row(selected_row, row_labels)
        status = _status_from_rows(marked_rows=marked_rows, ambiguous_rows=ambiguous_rows)
        manual_review_required = status in {"missing", "ambiguous"}
        return {
            "block_id": block.get("block_id"),
            "title": block.get("title"),
            "selection_mode": selection_mode,
            "rows": rows,
            "cols": cols,
            "selected": {
                "row_index": selected_row,
                "value": value,
                "marked_rows": marked_rows,
                "ambiguous_rows": ambiguous_rows,
                "status": status,
                "ratios_by_row": ratios,
            },
            "manual_review_required": manual_review_required,
        }

    for col in range(cols):
        col_items = by_col.get(col, [])
        selected_row, marked_rows, ambiguous_rows = _select_single_choice(
            bubble_results=col_items
        )
        value = _label_for_row(selected_row, row_labels)
        status = _status_from_rows(marked_rows=marked_rows, ambiguous_rows=ambiguous_rows)
        if status in {"missing", "ambiguous"}:
            manual_review_required = True
        ratios = {
            item.row: round(float(item.fill_ratio), 6)
            for item in col_items
        }
        column_results.append(
            {
                "column_index": col,
                "row_index": selected_row,
                "value": value,
                "marked_rows": marked_rows,
                "ambiguous_rows": ambiguous_rows,
                "status": status,
                "ratios_by_row": ratios,
            }
        )

    compact_value = "".join(
        item["value"] for item in column_results if isinstance(item.get("value"), str)
    )
    return {
        "block_id": block.get("block_id"),
        "title": block.get("title"),
        "selection_mode": selection_mode,
        "rows": rows,
        "cols": cols,
        "columns": column_results,
        "value": compact_value,
        "manual_review_required": manual_review_required,
    }


def _select_single_choice(
    *,
    bubble_results: list[BubbleReadResult],
) -> tuple[int | None, list[int], list[int]]:
    marked = [item for item in bubble_results if item.state == "marcada"]
    ambiguous = [item for item in bubble_results if item.state == "ambigua"]

    marked_rows = [item.row for item in marked]
    ambiguous_rows = [item.row for item in ambiguous]

    if len(marked) == 1:
        return marked[0].row, marked_rows, ambiguous_rows
    if len(marked) > 1:
        winner = max(marked, key=lambda item: float(item.fill_ratio))
        for item in marked:
            if item.row != winner.row and item.row not in ambiguous_rows:
                ambiguous_rows.append(item.row)
        return winner.row, marked_rows, sorted(set(ambiguous_rows))
    return None, marked_rows, sorted(set(ambiguous_rows))


def _label_for_row(row_index: int | None, row_labels: Any) -> str | None:
    if row_index is None:
        return None
    if isinstance(row_labels, list) and row_index < len(row_labels):
        return str(row_labels[row_index])
    return str(row_index)


def _status_from_rows(*, marked_rows: list[int], ambiguous_rows: list[int]) -> str:
    if len(marked_rows) == 0 and len(ambiguous_rows) == 0:
        return "missing"
    if len(marked_rows) > 1 or len(ambiguous_rows) > 0:
        return "ambiguous"
    return "ok"
