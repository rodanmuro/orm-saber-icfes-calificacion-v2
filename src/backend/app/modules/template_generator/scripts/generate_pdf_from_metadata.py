from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reportlab.lib.colors import Color
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.modules.template_generator.aruco_assets import build_aruco_image_reader


PRINTABLE_AREA_COLOR = Color(0.78, 0.78, 0.78)


def _invert_y(page_height_mm: float, y_mm: float) -> float:
    return page_height_mm - y_mm


def _draw_header_fields(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
) -> None:
    row1 = ["NOMBRE", "GRUPO", "ASIGNATURA"]
    row2 = ["TIPO DE DOCUMENTO", "NUMERO DE DOCUMENTO", "DOCENTE", "FECHA"]
    weights1 = [6.0, 2.0, 4.0]
    weights2 = [2.5, 4.5, 2.5, 1.5]

    pad_x_mm = 2.0
    pad_y_mm = 2.0
    row_gap_mm = 1.8
    font_name = "Helvetica"
    font_size_pt = 6.5
    label_line_gap_mm = 1.2

    inner_x_mm = x_mm + pad_x_mm
    inner_y_mm = y_mm + pad_y_mm
    inner_w_mm = max(1.0, width_mm - (2.0 * pad_x_mm))
    inner_h_mm = max(1.0, height_mm - (2.0 * pad_y_mm))
    row_h_mm = max(2.0, (inner_h_mm - row_gap_mm) / 2.0)

    def draw_row(labels: list[str], weights: list[float], row_top_mm: float) -> None:
        total = sum(weights)
        cursor_mm = inner_x_mm
        for label, w in zip(labels, weights, strict=False):
            field_w_mm = inner_w_mm * (w / total)
            text_baseline_y_mm = row_top_mm + (row_h_mm * 0.52)
            text_y_pt = _invert_y(page_height_mm, text_baseline_y_mm) * mm - (font_size_pt * 0.35)
            pdf.setFillColor(Color(0.25, 0.25, 0.25))
            pdf.setFont(font_name, font_size_pt)
            pdf.drawString(cursor_mm * mm, text_y_pt, f"{label}:")

            label_w_pt = pdf.stringWidth(f"{label}:", font_name, font_size_pt)
            line_start_mm = cursor_mm + (label_w_pt / mm) + label_line_gap_mm
            line_end_mm = cursor_mm + field_w_mm - 0.6
            if line_end_mm > line_start_mm:
                line_y_mm = text_baseline_y_mm + 0.8
                pdf.setLineWidth(0.4)
                pdf.line(
                    line_start_mm * mm,
                    _invert_y(page_height_mm, line_y_mm) * mm,
                    line_end_mm * mm,
                    _invert_y(page_height_mm, line_y_mm) * mm,
                )
            cursor_mm += field_w_mm
        pdf.setFillColorRGB(0, 0, 0)

    row1_top_mm = inner_y_mm
    row2_top_mm = inner_y_mm + row_h_mm + row_gap_mm
    draw_row(row1, weights1, row1_top_mm)
    draw_row(row2, weights2, row2_top_mm)


def _resolve_aux_label(cfg: dict[str, Any], row: int, col: int) -> str:
    row_labels = cfg.get("row_labels")
    col_labels = cfg.get("col_labels")
    if cfg.get("cols") == 1 and isinstance(row_labels, list) and row < len(row_labels):
        return str(row_labels[row])
    if cfg.get("rows") == 10 and isinstance(row_labels, list) and row < len(row_labels):
        return str(row_labels[row])
    if isinstance(col_labels, list) and col < len(col_labels):
        return str(col_labels[col])
    return ""


def _draw_document_type_labels_left(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    cfg: dict[str, Any],
    bubble_center_x_mm: float,
    center_y_mm: float,
    row: int,
) -> None:
    row_labels = cfg.get("row_labels")
    if not isinstance(row_labels, list) or row >= len(row_labels):
        return
    label = str(row_labels[row])
    font_name = "Helvetica"
    font_size = 8.5
    gap_mm = 4.0
    pdf.setFillColor(Color(0.5, 0.5, 0.5))
    pdf.setFont(font_name, font_size)
    text_width = pdf.stringWidth(label, font_name, font_size)
    text_x = (bubble_center_x_mm - gap_mm) * mm - text_width
    text_y = _invert_y(page_height_mm, center_y_mm) * mm - (font_size * 0.35)
    pdf.drawString(text_x, text_y, label)
    pdf.setFillColorRGB(0, 0, 0)


def render_pdf_from_metadata(metadata: dict[str, Any], output_path: Path) -> Path:
    page = metadata["page"]
    page_width_mm = float(page["width_mm"])
    page_height_mm = float(page["height_mm"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=(page_width_mm * mm, page_height_mm * mm))
    pdf.setTitle(f"Template {metadata.get('template_id')} v{metadata.get('version')}")

    printable = metadata.get("printable_area")
    if isinstance(printable, dict):
        pdf.setStrokeColor(PRINTABLE_AREA_COLOR)
        pdf.setLineWidth(0.6)
        pdf.rect(
            float(printable["x_mm"]) * mm,
            _invert_y(page_height_mm, float(printable["y_mm"]) + float(printable["height_mm"])) * mm,
            float(printable["width_mm"]) * mm,
            float(printable["height_mm"]) * mm,
        )
        pdf.setStrokeColorRGB(0, 0, 0)

    main_block = metadata.get("block")
    if isinstance(main_block, dict):
        pdf.setLineWidth(1.0)
        pdf.rect(
            float(main_block["x_mm"]) * mm,
            _invert_y(page_height_mm, float(main_block["y_mm"]) + float(main_block["height_mm"])) * mm,
            float(main_block["width_mm"]) * mm,
            float(main_block["height_mm"]) * mm,
        )

    for marker in metadata.get("aruco_markers", []):
        size_mm = float(marker["size_mm"])
        x_mm = float(marker["center_x_mm"]) - (size_mm / 2.0)
        y_mm = float(marker["center_y_mm"]) - (size_mm / 2.0)
        marker_px = max(64, int(size_mm * 12))
        marker_img = build_aruco_image_reader(
            dictionary_name=str(metadata.get("aruco_dictionary_name")),
            marker_id=int(marker["marker_id"]),
            marker_pixels=marker_px,
        )
        pdf.drawImage(
            marker_img,
            x_mm * mm,
            _invert_y(page_height_mm, y_mm + size_mm) * mm,
            width=size_mm * mm,
            height=size_mm * mm,
            preserveAspectRatio=True,
            mask="auto",
        )

    for block in metadata.get("auxiliary_blocks", []):
        x_mm = float(block["x_mm"])
        y_mm = float(block["y_mm"])
        width_mm = float(block["width_mm"])
        height_mm = float(block["height_mm"])
        block_id = str(block.get("block_id", ""))
        title = str(block.get("title", ""))
        pdf.setLineWidth(0.8)
        pdf.rect(
            x_mm * mm,
            _invert_y(page_height_mm, y_mm + height_mm) * mm,
            width_mm * mm,
            height_mm * mm,
        )
        if block_id == "header":
            _draw_header_fields(
                pdf,
                page_height_mm=page_height_mm,
                x_mm=x_mm,
                y_mm=y_mm,
                width_mm=width_mm,
                height_mm=height_mm,
            )
        else:
            pdf.setFillColor(Color(0.35, 0.35, 0.35))
            pdf.setFont("Helvetica", 7)
            pdf.drawString(
                (x_mm + 1.5) * mm,
                _invert_y(page_height_mm, y_mm + 3.0) * mm,
                title,
            )
            pdf.setFillColorRGB(0, 0, 0)

        if str(block.get("block_type")) != "omr":
            continue
        cfg = block.get("omr_config")
        if not isinstance(cfg, dict):
            continue
        rows = int(cfg["rows"])
        cols = int(cfg["cols"])
        diameter = float(cfg["bubble_diameter_mm"])
        radius = diameter / 2.0
        spacing_x = float(cfg["spacing_x_mm"])
        spacing_y = float(cfg["spacing_y_mm"])
        grid_width = diameter + (cols - 1) * spacing_x
        grid_height = diameter + (rows - 1) * spacing_y
        left_padding = cfg.get("left_padding_mm")
        top_padding = cfg.get("top_padding_mm")
        if left_padding is None:
            origin_x = x_mm + (width_mm - grid_width) / 2.0
        else:
            origin_x = x_mm + float(left_padding)
        if top_padding is None:
            origin_y = y_mm + (height_mm - grid_height) / 2.0
        else:
            origin_y = y_mm + float(top_padding)
        pdf.setLineWidth(0.7)
        for row in range(rows):
            for col in range(cols):
                cx = origin_x + radius + col * spacing_x
                cy = origin_y + radius + row * spacing_y
                pdf.circle(cx * mm, _invert_y(page_height_mm, cy) * mm, radius * mm, stroke=1, fill=0)
                if str(block.get("block_id")) == "document_type" and cols == 1:
                    _draw_document_type_labels_left(
                        pdf,
                        page_height_mm=page_height_mm,
                        cfg=cfg,
                        bubble_center_x_mm=cx,
                        center_y_mm=cy,
                        row=row,
                    )
                    continue
                label = _resolve_aux_label(cfg, row, col)
                if label:
                    pdf.setFillColor(Color(0.55, 0.55, 0.55))
                    pdf.setFont("Helvetica", 7.6)
                    text_width = pdf.stringWidth(label, "Helvetica", 7.6)
                    pdf.drawString(
                        (cx * mm) - (text_width / 2.0),
                        _invert_y(page_height_mm, cy) * mm - 2.1,
                        label,
                    )
                    pdf.setFillColorRGB(0, 0, 0)

    label_style = metadata.get("bubble_label_style", {})
    label_gray = float(label_style.get("gray_level", 0.78))
    label_font = str(label_style.get("font_name", "Helvetica"))
    label_size = float(label_style.get("font_size_pt", 8.0))

    number_style = metadata.get("question_number_style", {})
    number_enabled = bool(number_style.get("enabled", True))
    number_gray = float(number_style.get("gray_level", 0.40))
    number_font = str(number_style.get("font_name", "Helvetica"))
    number_size = float(number_style.get("font_size_pt", 8.0))

    pdf.setLineWidth(0.7)
    for item in metadata.get("question_items", []):
        if number_enabled:
            value = str(item.get("question_number"))
            pdf.setFillColor(Color(number_gray, number_gray, number_gray))
            pdf.setFont(number_font, number_size)
            tw = pdf.stringWidth(value, number_font, number_size)
            tx = float(item["number_center_x_mm"]) * mm - (tw / 2.0)
            ty = _invert_y(page_height_mm, float(item["number_center_y_mm"])) * mm - (number_size * 0.35)
            pdf.drawString(tx, ty, value)
            pdf.setFillColorRGB(0, 0, 0)

        for opt in item.get("options", []):
            cx = float(opt["center_x_mm"])
            cy = float(opt["center_y_mm"])
            radius = float(opt["radius_mm"])
            pdf.circle(cx * mm, _invert_y(page_height_mm, cy) * mm, radius * mm, stroke=1, fill=0)
            label = str(opt.get("label", ""))
            pdf.setFillColor(Color(label_gray, label_gray, label_gray))
            pdf.setFont(label_font, label_size)
            tw = pdf.stringWidth(label, label_font, label_size)
            tx = cx * mm - (tw / 2.0)
            ty = _invert_y(page_height_mm, cy) * mm - (label_size * 0.35)
            pdf.drawString(tx, ty, label)
            pdf.setFillColorRGB(0, 0, 0)

    pdf.showPage()
    pdf.save()
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PDF strictly from metadata JSON")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    out = render_pdf_from_metadata(metadata=metadata, output_path=Path(args.output))
    print(f"PDF from metadata: {out}")


if __name__ == "__main__":
    main()
