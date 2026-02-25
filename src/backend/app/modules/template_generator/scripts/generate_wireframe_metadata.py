from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.modules.template_generator.aruco_renderer import build_aruco_layout
from app.modules.template_generator.config_loader import load_template_config
from app.modules.template_generator.geometry import compute_printable_area


def _marker_square(marker) -> tuple[float, float, float, float]:
    half = marker.size_mm / 2.0
    x_left = marker.center_x_mm - half
    y_top = marker.center_y_mm - half
    x_right = marker.center_x_mm + half
    y_bottom = marker.center_y_mm + half
    return x_left, y_top, x_right, y_bottom


def build_wireframe_metadata(
    *,
    config_path: Path,
    header_height_mm: float = 20.0,
    header_to_top_boxes_gap_mm: float = 10.0,
    top_left_box_width_mm: float = 92.0,
    top_boxes_height_mm: float = 88.0,
    top_boxes_gap_mm: float = 10.0,
    top_boxes_to_bottom_gap_mm: float = 10.0,
    top_left_expand_left_mm: float = 10.0,
    id_grid_left_padding_mm: float = 5.0,
    top_right_expand_right_mm: float = 10.0,
    right_grid_left_padding_mm: float = 5.0,
    bottom_expand_left_mm: float = 10.0,
    bottom_expand_right_mm: float = 10.0,
    bottom_to_lower_markers_gap_mm: float = 5.0,
) -> dict[str, Any]:
    cfg = load_template_config(config_path)
    printable_area = compute_printable_area(cfg.page_config)
    markers = build_aruco_layout(printable_area, cfg.aruco_config)
    marker_by_corner = {item.corner: item for item in markers}

    tl = _marker_square(marker_by_corner["top_left"])
    tr = _marker_square(marker_by_corner["top_right"])
    bl = _marker_square(marker_by_corner["bottom_left"])
    br = _marker_square(marker_by_corner["bottom_right"])

    left_inner_mm = max(tl[2], bl[2])
    right_inner_mm = min(tr[0], br[0])
    top_inner_mm = max(tl[3], tr[3])
    bottom_inner_mm = min(bl[1], br[1])

    inner_width_mm = right_inner_mm - left_inner_mm
    inner_height_mm = bottom_inner_mm - top_inner_mm
    if inner_width_mm <= 0 or inner_height_mm <= 0:
        raise ValueError("invalid inner bounds from ArUco markers")

    left_box_x_mm = left_inner_mm - top_left_expand_left_mm
    if left_box_x_mm < printable_area.x_mm:
        raise ValueError("left top box expansion exceeds printable area")
    student_box_width_mm = top_left_box_width_mm + top_left_expand_left_mm

    top_lane_left_mm = left_box_x_mm
    top_lane_right_mm = right_inner_mm + top_right_expand_right_mm
    printable_right_mm = printable_area.x_mm + printable_area.width_mm
    if top_lane_right_mm > printable_right_mm:
        raise ValueError("top lane right boundary exceeds printable area")

    previous_exam_box_width_mm = (
        right_inner_mm - (left_box_x_mm + student_box_width_mm + top_boxes_gap_mm)
    ) + top_right_expand_right_mm
    exam_box_width_mm = previous_exam_box_width_mm - 24.0
    if exam_box_width_mm <= 0:
        raise ValueError("exam box width is <= 0 after reducing 3 columns")

    gap_new_student_mm = 5.0
    gap_student_exam_mm = 5.0
    new_left_box_width_mm = (
        (top_lane_right_mm - top_lane_left_mm)
        - student_box_width_mm
        - exam_box_width_mm
        - gap_new_student_mm
        - gap_student_exam_mm
    )
    if new_left_box_width_mm <= 0:
        raise ValueError("new left box width is <= 0; adjust dimensions")

    new_left_box_x_mm = top_lane_left_mm
    student_box_x_mm = new_left_box_x_mm + new_left_box_width_mm + gap_new_student_mm
    exam_box_x_mm = student_box_x_mm + student_box_width_mm + gap_student_exam_mm

    header_y_mm = printable_area.y_mm
    top_boxes_y_mm = header_y_mm + header_height_mm + header_to_top_boxes_gap_mm
    bottom_box_y_mm = top_boxes_y_mm + top_boxes_height_mm + top_boxes_to_bottom_gap_mm
    bottom_box_x_mm = left_inner_mm - bottom_expand_left_mm
    bottom_box_width_mm = inner_width_mm + bottom_expand_left_mm + bottom_expand_right_mm
    if bottom_box_x_mm < printable_area.x_mm:
        raise ValueError("bottom box expansion exceeds printable area on the left")
    if bottom_box_x_mm + bottom_box_width_mm > printable_right_mm:
        raise ValueError("bottom box expansion exceeds printable area on the right")

    bottom_limit_mm = bottom_inner_mm - bottom_to_lower_markers_gap_mm
    bottom_box_height_mm = bottom_limit_mm - bottom_box_y_mm
    if bottom_box_height_mm <= 0:
        raise ValueError("bottom box height is <= 0; reduce heights/gaps or increase page space")

    # Header shrink from wireframe script.
    header_shrink_side_mm = 5.0
    header_shrink_top_mm = 5.0
    header_box_x_mm = left_inner_mm + header_shrink_side_mm
    header_box_y_mm = header_y_mm + header_shrink_top_mm
    header_box_w_mm = inner_width_mm - (2.0 * header_shrink_side_mm)
    header_box_h_mm = header_height_mm - header_shrink_top_mm

    # Document block bubbles (1 x 7, centered with right-aligned labels).
    doc_labels = ["RC", "TI", "CC", "CE", "PA", "PPT", "OTRO"]
    doc_diameter = 4.0
    doc_spacing = 8.0
    doc_radius = doc_diameter / 2.0
    doc_rows = len(doc_labels)
    doc_block_h = doc_diameter + (doc_rows - 1) * doc_spacing
    # Keep label width approximation coherent with draw script.
    # Value tuned to reproduce the same bubble lane used in wireframe.
    doc_max_label_width_mm = 6.0
    doc_label_to_bubble_gap_mm = 4.0
    doc_bubble_shift_right_mm = 8.0
    doc_block_w = doc_max_label_width_mm + doc_label_to_bubble_gap_mm + doc_diameter
    doc_origin_x = new_left_box_x_mm + (new_left_box_width_mm - doc_block_w) / 2.0
    doc_origin_y = top_boxes_y_mm + (top_boxes_height_mm - doc_block_h) / 2.0
    doc_bubble_center_x = (
        doc_origin_x
        + doc_max_label_width_mm
        + doc_label_to_bubble_gap_mm
        + doc_radius
        + doc_bubble_shift_right_mm
    )

    # Student/exam grid vertical alignment.
    id_rows = 10
    id_cols = 12
    id_diameter = 4.0
    id_spacing = 8.0
    id_radius = id_diameter / 2.0
    id_grid_h = id_diameter + (id_rows - 1) * id_spacing
    id_origin_y = top_boxes_y_mm + (top_boxes_height_mm - id_grid_h) / 2.0
    id_origin_x = student_box_x_mm + id_grid_left_padding_mm

    ex_rows = 10
    ex_cols = 4
    ex_diameter = 4.0
    ex_spacing = 8.0
    ex_radius = ex_diameter / 2.0
    ex_origin_x = exam_box_x_mm + right_grid_left_padding_mm
    ex_origin_y = id_origin_y

    # Answers grid from wireframe.
    ans_rows = 10
    ans_cols = 4
    ans_diameter = 4.0
    ans_radius = ans_diameter / 2.0
    ans_spacing = 8.0
    number_gap = 6.5
    question_col_gap = 8.0
    question_width = number_gap + ans_diameter + (3 * ans_spacing)
    total_width = ans_cols * question_width + (ans_cols - 1) * question_col_gap
    ans_grid_h = ans_diameter + (ans_rows - 1) * ans_spacing
    ans_origin_x = bottom_box_x_mm + (bottom_box_width_mm - total_width) / 2.0
    ans_origin_y = bottom_box_y_mm + (bottom_box_height_mm - ans_grid_h) / 2.0

    bubbles: list[dict[str, Any]] = []
    question_numbers: list[dict[str, Any]] = []
    question_items: list[dict[str, Any]] = []
    qn = 1
    for col in range(ans_cols):
        col_base_x = ans_origin_x + col * (question_width + question_col_gap)
        first_bubble_center_x = col_base_x + number_gap + ans_radius
        for row in range(ans_rows):
            center_y = ans_origin_y + ans_radius + row * ans_spacing
            options = []
            for b, label in enumerate(["A", "B", "C", "D"]):
                cx = first_bubble_center_x + b * ans_spacing
                bubble_id = f"R{col+1:02d}_{row:02d}_{label}"
                option = {
                    "bubble_id": bubble_id,
                    "group_id": f"R{col+1:02d}",
                    "row": row,
                    "col": b,
                    "label": label,
                    "center_x_mm": round(cx, 6),
                    "center_y_mm": round(center_y, 6),
                    "radius_mm": round(ans_radius, 6),
                }
                bubbles.append(option.copy())
                options.append(option)

            num_center_x = first_bubble_center_x - number_gap
            question_numbers.append(
                {
                    "group_id": f"R{col+1:02d}",
                    "row": row,
                    "question_number": qn,
                    "center_x_mm": round(num_center_x, 6),
                    "center_y_mm": round(center_y, 6),
                }
            )
            question_items.append(
                {
                    "group_id": f"R{col+1:02d}",
                    "row": row,
                    "question_number": qn,
                    "number_center_x_mm": round(num_center_x, 6),
                    "number_center_y_mm": round(center_y, 6),
                    "options": options,
                }
            )
            qn += 1

    payload = {
        "template_id": f"{cfg.output_config.template_id}_wireframe",
        "version": f"{cfg.output_config.version}_wireframe",
        "aruco_dictionary_name": cfg.aruco_config.dictionary_name,
        "page": cfg.page_config.model_dump(),
        "printable_area": printable_area.model_dump(),
        "main_block_bbox": {
            "x_mm": round(bottom_box_x_mm, 6),
            "y_mm": round(bottom_box_y_mm, 6),
            "width_mm": round(bottom_box_width_mm, 6),
            "height_mm": round(bottom_box_height_mm, 6),
        },
        "block": {
            "x_mm": round(bottom_box_x_mm, 6),
            "y_mm": round(bottom_box_y_mm, 6),
            "width_mm": round(bottom_box_width_mm, 6),
            "height_mm": round(bottom_box_height_mm, 6),
        },
        "aruco_markers": [m.model_dump() for m in markers],
        "bubbles": bubbles,
        "bubble_label_style": {
            "gray_level": 0.62,
            "font_name": "Helvetica",
            "font_size_pt": 5.5,
        },
        "question_numbers": question_numbers,
        "question_number_style": {
            "enabled": True,
            "center_gap_mm": 6.5,
            "gray_level": 0.62,
            "font_name": "Helvetica",
            "font_size_pt": 6.0,
        },
        "question_items": question_items,
        "auxiliary_blocks": [
            {
                "block_id": "header",
                "title": "HEADER",
                "block_type": "handwrite",
                "x_mm": round(header_box_x_mm, 6),
                "y_mm": round(header_box_y_mm, 6),
                "width_mm": round(header_box_w_mm, 6),
                "height_mm": round(header_box_h_mm, 6),
                "omr_config": None,
            },
            {
                "block_id": "document_type",
                "title": "DOCUMENTO",
                "block_type": "omr",
                "x_mm": round(new_left_box_x_mm, 6),
                "y_mm": round(top_boxes_y_mm, 6),
                "width_mm": round(new_left_box_width_mm, 6),
                "height_mm": round(top_boxes_height_mm, 6),
                "omr_config": {
                    "rows": 7,
                    "cols": 1,
                    "bubble_diameter_mm": 4.0,
                    "spacing_x_mm": 8.0,
                    "spacing_y_mm": 8.0,
                    "selection_mode": "single_choice",
                    "row_labels": doc_labels,
                    "col_labels": None,
                    "notes": "wireframe-derived",
                },
            },
            {
                "block_id": "student_identity_number",
                "title": "NUMERO DE IDENTIDAD",
                "block_type": "omr",
                "x_mm": round(student_box_x_mm, 6),
                "y_mm": round(top_boxes_y_mm, 6),
                "width_mm": round(student_box_width_mm, 6),
                "height_mm": round(top_boxes_height_mm, 6),
                "omr_config": {
                    "rows": id_rows,
                    "cols": id_cols,
                    "bubble_diameter_mm": id_diameter,
                    "spacing_x_mm": id_spacing,
                    "spacing_y_mm": id_spacing,
                    "selection_mode": "single_per_column",
                    "row_labels": [str(i) for i in range(10)],
                    "col_labels": None,
                    "notes": "wireframe-derived",
                    "left_padding_mm": id_grid_left_padding_mm,
                    "top_padding_mm": round(id_origin_y - top_boxes_y_mm, 6),
                },
            },
            {
                "block_id": "exam_identifier",
                "title": "IDENTIFICACION EXAMEN",
                "block_type": "omr",
                "x_mm": round(exam_box_x_mm, 6),
                "y_mm": round(top_boxes_y_mm, 6),
                "width_mm": round(exam_box_width_mm, 6),
                "height_mm": round(top_boxes_height_mm, 6),
                "omr_config": {
                    "rows": ex_rows,
                    "cols": ex_cols,
                    "bubble_diameter_mm": ex_diameter,
                    "spacing_x_mm": ex_spacing,
                    "spacing_y_mm": ex_spacing,
                    "selection_mode": "single_per_column",
                    "row_labels": [str(i) for i in range(10)],
                    "col_labels": None,
                    "notes": "wireframe-derived",
                    "left_padding_mm": right_grid_left_padding_mm,
                    "top_padding_mm": round(ex_origin_y - top_boxes_y_mm, 6),
                },
            },
        ],
    }

    # Force explicit document_type first bubble center to match wireframe equations used for drawing.
    payload["auxiliary_blocks"][1]["omr_config"]["left_padding_mm"] = round(
        doc_bubble_center_x - new_left_box_x_mm - doc_radius, 6
    )
    payload["auxiliary_blocks"][1]["omr_config"]["top_padding_mm"] = round(
        doc_origin_y - top_boxes_y_mm, 6
    )

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate metadata JSON from wireframe geometry")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to template config JSON (e.g. config/template.basica_omr_v2.json)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output metadata JSON path",
    )
    args = parser.parse_args()

    metadata = build_wireframe_metadata(config_path=Path(args.config))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wireframe metadata JSON: {output}")


if __name__ == "__main__":
    main()
