from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.modules.template_generator.aruco_assets import build_aruco_image_reader
from app.modules.template_generator.aruco_renderer import build_aruco_layout
from app.modules.template_generator.config_loader import load_template_config
from app.modules.template_generator.geometry import compute_printable_area

PRINTABLE_AREA_COLOR = Color(0.78, 0.78, 0.78)
BUBBLE_TEXT_COLOR = Color(0.62, 0.62, 0.62)


def _invert_y(page_height_mm: float, y_mm: float) -> float:
    return page_height_mm - y_mm


def _marker_square(marker) -> tuple[float, float, float, float]:
    half = marker.size_mm / 2.0
    x_left = marker.center_x_mm - half
    y_top = marker.center_y_mm - half
    x_right = marker.center_x_mm + half
    y_bottom = marker.center_y_mm + half
    return x_left, y_top, x_right, y_bottom


def _draw_markers(pdf: canvas.Canvas, *, page_height_mm: float, dictionary_name: str, markers: list) -> None:
    for marker in markers:
        x_left, y_top, _, _ = _marker_square(marker)
        marker_px = max(64, int(marker.size_mm * 12))
        marker_img = build_aruco_image_reader(
            dictionary_name=dictionary_name,
            marker_id=marker.marker_id,
            marker_pixels=marker_px,
        )
        pdf.drawImage(
            marker_img,
            x_left * mm,
            _invert_y(page_height_mm, y_top + marker.size_mm) * mm,
            width=marker.size_mm * mm,
            height=marker.size_mm * mm,
            preserveAspectRatio=True,
            mask="auto",
        )
        pdf.setLineWidth(0.4)
        pdf.rect(
            x_left * mm,
            _invert_y(page_height_mm, y_top + marker.size_mm) * mm,
            marker.size_mm * mm,
            marker.size_mm * mm,
            stroke=1,
            fill=0,
        )


def _draw_rect(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    label: str,
) -> None:
    pdf.setLineWidth(1)
    pdf.rect(
        x_mm * mm,
        _invert_y(page_height_mm, y_mm + height_mm) * mm,
        width_mm * mm,
        height_mm * mm,
    )
    if label:
        pdf.setFont("Helvetica", 7)
        pdf.drawString((x_mm + 1.2) * mm, _invert_y(page_height_mm, y_mm + 2.6) * mm, label)


def _draw_id_bubble_grid(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    box_x_mm: float,
    box_y_mm: float,
    box_width_mm: float,
    box_height_mm: float,
    cols: int = 12,
    rows: int = 10,
    bubble_diameter_mm: float = 4.0,
    spacing_mm: float = 8.0,
    start_from_left_mm: float | None = None,
) -> None:
    radius_mm = bubble_diameter_mm / 2.0
    grid_width_mm = bubble_diameter_mm + (cols - 1) * spacing_mm
    grid_height_mm = bubble_diameter_mm + (rows - 1) * spacing_mm

    if grid_width_mm > box_width_mm or grid_height_mm > box_height_mm:
        raise ValueError("ID bubble grid does not fit inside left top box")

    if start_from_left_mm is None:
        origin_x_mm = box_x_mm + (box_width_mm - grid_width_mm) / 2.0
    else:
        origin_x_mm = box_x_mm + start_from_left_mm
        if origin_x_mm + grid_width_mm > box_x_mm + box_width_mm:
            raise ValueError("ID bubble grid overflows box width with the requested left offset")
    origin_y_mm = box_y_mm + (box_height_mm - grid_height_mm) / 2.0

    pdf.setLineWidth(0.6)
    pdf.setFont("Helvetica", 6)
    pdf.setFillColor(BUBBLE_TEXT_COLOR)
    for row in range(rows):
        digit = str(row)
        for col in range(cols):
            center_x_mm = origin_x_mm + radius_mm + col * spacing_mm
            center_y_mm = origin_y_mm + radius_mm + row * spacing_mm
            pdf.circle(
                center_x_mm * mm,
                _invert_y(page_height_mm, center_y_mm) * mm,
                radius_mm * mm,
                stroke=1,
                fill=0,
            )
            text_width = pdf.stringWidth(digit, "Helvetica", 6)
            text_x = center_x_mm * mm - (text_width / 2.0)
            text_y = _invert_y(page_height_mm, center_y_mm) * mm - (6 * 0.35)
            pdf.drawString(text_x, text_y, digit)
    pdf.setFillColorRGB(0, 0, 0)


def _draw_right_bubble_grid(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    box_x_mm: float,
    box_y_mm: float,
    box_width_mm: float,
    box_height_mm: float,
    left_padding_mm: float = 5.0,
    bubble_diameter_mm: float = 4.0,
    spacing_mm: float = 8.0,
    aligned_origin_y_mm: float | None = None,
    forced_cols: int | None = None,
    forced_rows: int | None = None,
) -> tuple[int, int]:
    radius_mm = bubble_diameter_mm / 2.0
    rows = int((box_height_mm - bubble_diameter_mm) // spacing_mm) + 1
    cols = int((box_width_mm - left_padding_mm - bubble_diameter_mm) // spacing_mm) + 1
    if forced_cols is not None:
        cols = min(cols, forced_cols)
    if forced_rows is not None:
        rows = min(rows, forced_rows)
    rows = max(rows, 0)
    cols = max(cols, 0)
    if rows == 0 or cols == 0:
        return (0, 0)

    origin_x_mm = box_x_mm + left_padding_mm
    if aligned_origin_y_mm is None:
        grid_height_mm = bubble_diameter_mm + (rows - 1) * spacing_mm
        origin_y_mm = box_y_mm + (box_height_mm - grid_height_mm) / 2.0
    else:
        origin_y_mm = aligned_origin_y_mm
        max_bottom = origin_y_mm + bubble_diameter_mm + (rows - 1) * spacing_mm
        if max_bottom > box_y_mm + box_height_mm:
            rows = int((box_y_mm + box_height_mm - origin_y_mm - bubble_diameter_mm) // spacing_mm) + 1
            rows = max(rows, 0)
            if rows == 0:
                return (0, 0)

    pdf.setLineWidth(0.6)
    pdf.setFont("Helvetica", 6)
    pdf.setFillColor(BUBBLE_TEXT_COLOR)
    for row in range(rows):
        digit = str(row % 10)
        for col in range(cols):
            center_x_mm = origin_x_mm + radius_mm + col * spacing_mm
            center_y_mm = origin_y_mm + radius_mm + row * spacing_mm
            pdf.circle(
                center_x_mm * mm,
                _invert_y(page_height_mm, center_y_mm) * mm,
                radius_mm * mm,
                stroke=1,
                fill=0,
            )
            text_width = pdf.stringWidth(digit, "Helvetica", 6)
            text_x = center_x_mm * mm - (text_width / 2.0)
            text_y = _invert_y(page_height_mm, center_y_mm) * mm - (6 * 0.35)
            pdf.drawString(text_x, text_y, digit)
    pdf.setFillColorRGB(0, 0, 0)

    return (cols, rows)


def _draw_answers_grid(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    box_x_mm: float,
    box_y_mm: float,
    box_width_mm: float,
    box_height_mm: float,
    rows: int = 10,
    cols: int = 4,
    bubble_diameter_mm: float = 4.0,
    bubble_spacing_mm: float = 8.0,
    number_gap_mm: float = 6.5,
    question_col_gap_mm: float = 8.0,
) -> None:
    radius_mm = bubble_diameter_mm / 2.0
    row_height_mm = bubble_spacing_mm
    grid_height_mm = bubble_diameter_mm + (rows - 1) * row_height_mm
    question_width_mm = number_gap_mm + bubble_diameter_mm + (3 * bubble_spacing_mm)
    total_width_mm = cols * question_width_mm + (cols - 1) * question_col_gap_mm

    if total_width_mm > box_width_mm or grid_height_mm > box_height_mm:
        raise ValueError("answers grid does not fit in response box")

    origin_x_mm = box_x_mm + (box_width_mm - total_width_mm) / 2.0
    origin_y_mm = box_y_mm + (box_height_mm - grid_height_mm) / 2.0

    pdf.setLineWidth(0.6)
    pdf.setFont("Helvetica", 6)
    label_font_size = 5.5
    labels = ["A", "B", "C", "D"]
    pdf.setFillColor(BUBBLE_TEXT_COLOR)

    for col in range(cols):
        col_base_x_mm = origin_x_mm + col * (question_width_mm + question_col_gap_mm)
        first_bubble_center_x_mm = col_base_x_mm + number_gap_mm + radius_mm
        for row in range(rows):
            center_y_mm = origin_y_mm + radius_mm + row * row_height_mm
            question_number = (col * rows) + row + 1
            q_text = str(question_number)
            q_text_w = pdf.stringWidth(q_text, "Helvetica", 6)
            q_text_x = (first_bubble_center_x_mm - number_gap_mm) * mm - (q_text_w / 2.0)
            q_text_y = _invert_y(page_height_mm, center_y_mm) * mm - (6 * 0.35)
            pdf.drawString(q_text_x, q_text_y, q_text)

            for b in range(4):
                bubble_center_x_mm = first_bubble_center_x_mm + b * bubble_spacing_mm
                pdf.circle(
                    bubble_center_x_mm * mm,
                    _invert_y(page_height_mm, center_y_mm) * mm,
                    radius_mm * mm,
                    stroke=1,
                    fill=0,
                )
                label = labels[b]
                label_w = pdf.stringWidth(label, "Helvetica", label_font_size)
                label_x = bubble_center_x_mm * mm - (label_w / 2.0)
                label_y = _invert_y(page_height_mm, center_y_mm) * mm - (label_font_size * 0.35)
                pdf.setFont("Helvetica", label_font_size)
                pdf.drawString(label_x, label_y, label)
                pdf.setFont("Helvetica", 6)
    pdf.setFillColorRGB(0, 0, 0)


def _draw_document_type_omr(
    pdf: canvas.Canvas,
    *,
    page_height_mm: float,
    box_x_mm: float,
    box_y_mm: float,
    box_width_mm: float,
    box_height_mm: float,
    options: list[str] | None = None,
    bubble_diameter_mm: float = 4.0,
    spacing_mm: float = 8.0,
    label_to_bubble_gap_mm: float = 4.0,
) -> None:
    if options is None:
        options = ["RC", "TI", "CC", "CE", "PA", "PPT", "OTRO"]
    if not options:
        return

    radius_mm = bubble_diameter_mm / 2.0
    rows = len(options)
    block_height_mm = bubble_diameter_mm + (rows - 1) * spacing_mm

    font_name = "Helvetica"
    font_size_pt = 7
    max_label_width_pt = max(pdf.stringWidth(label, font_name, font_size_pt) for label in options)
    max_label_width_mm = max_label_width_pt / mm
    block_width_mm = max_label_width_mm + label_to_bubble_gap_mm + bubble_diameter_mm

    if block_width_mm > box_width_mm or block_height_mm > box_height_mm:
        raise ValueError("document type OMR block does not fit in left top box")

    origin_x_mm = box_x_mm + (box_width_mm - block_width_mm) / 2.0
    origin_y_mm = box_y_mm + (box_height_mm - block_height_mm) / 2.0

    label_x_mm = origin_x_mm
    bubble_center_x_mm = origin_x_mm + max_label_width_mm + label_to_bubble_gap_mm + radius_mm

    pdf.setLineWidth(0.6)
    pdf.setFont(font_name, font_size_pt)
    for idx, label in enumerate(options):
        center_y_mm = origin_y_mm + radius_mm + idx * spacing_mm
        text_width_pt = pdf.stringWidth(label, font_name, font_size_pt)
        # Right-align labels so all bubbles form a clean vertical line.
        text_x_pt = (label_x_mm + max_label_width_mm) * mm - text_width_pt
        text_y_pt = _invert_y(page_height_mm, center_y_mm) * mm - (font_size_pt * 0.35)
        pdf.drawString(text_x_pt, text_y_pt, label)
        pdf.circle(
            bubble_center_x_mm * mm,
            _invert_y(page_height_mm, center_y_mm) * mm,
            radius_mm * mm,
            stroke=1,
            fill=0,
        )


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
            text_y_pt = _invert_y(page_height_mm, text_baseline_y_mm) * mm - (
                font_size_pt * 0.35
            )
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

    row1_top_mm = inner_y_mm
    row2_top_mm = inner_y_mm + row_h_mm + row_gap_mm
    draw_row(row1, weights1, row1_top_mm)
    draw_row(row2, weights2, row2_top_mm)


def generate_wireframe_pdf(
    *,
    config_path: Path,
    output_path: Path,
    header_height_mm: float,
    header_to_top_boxes_gap_mm: float,
    top_left_box_width_mm: float,
    top_boxes_height_mm: float,
    top_boxes_gap_mm: float,
    top_boxes_to_bottom_gap_mm: float,
    top_left_expand_left_mm: float,
    id_grid_left_padding_mm: float,
    top_right_expand_right_mm: float,
    right_grid_left_padding_mm: float,
    bottom_expand_left_mm: float,
    bottom_expand_right_mm: float,
    bottom_to_lower_markers_gap_mm: float,
) -> Path:
    config = load_template_config(config_path)
    printable_area = compute_printable_area(config.page_config)
    markers = build_aruco_layout(printable_area, config.aruco_config)
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

    # Exam box reduced by 3 horizontal columns (3 * spacing=24 mm) compared to previous layout.
    previous_exam_box_width_mm = (right_inner_mm - (left_box_x_mm + student_box_width_mm + top_boxes_gap_mm)) + top_right_expand_right_mm
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
    printable_right_mm = printable_area.x_mm + printable_area.width_mm
    if bottom_box_x_mm < printable_area.x_mm:
        raise ValueError("bottom box expansion exceeds printable area on the left")
    if bottom_box_x_mm + bottom_box_width_mm > printable_right_mm:
        raise ValueError("bottom box expansion exceeds printable area on the right")

    bottom_limit_mm = bottom_inner_mm - bottom_to_lower_markers_gap_mm
    bottom_box_height_mm = bottom_limit_mm - bottom_box_y_mm
    if bottom_box_height_mm <= 0:
        raise ValueError("bottom box height is <= 0; reduce heights/gaps or increase page space")

    page_width_pt = config.page_config.width_mm * mm
    page_height_pt = config.page_config.height_mm * mm
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=(page_width_pt, page_height_pt))
    pdf.setTitle("Template wireframe (Aruco + Rectangles)")

    # Printable area guide.
    pdf.setStrokeColor(PRINTABLE_AREA_COLOR)
    pdf.setLineWidth(0.6)
    pdf.rect(
        printable_area.x_mm * mm,
        _invert_y(config.page_config.height_mm, printable_area.y_mm + printable_area.height_mm) * mm,
        printable_area.width_mm * mm,
        printable_area.height_mm * mm,
    )
    pdf.setStrokeColorRGB(0, 0, 0)

    _draw_markers(
        pdf,
        page_height_mm=config.page_config.height_mm,
        dictionary_name=config.aruco_config.dictionary_name,
        markers=markers,
    )

    # Header + top row of boxes + bottom response box.
    header_shrink_side_mm = 5.0
    header_shrink_top_mm = 5.0
    header_box_x_mm = left_inner_mm + header_shrink_side_mm
    header_box_y_mm = header_y_mm + header_shrink_top_mm
    header_box_w_mm = inner_width_mm - (2.0 * header_shrink_side_mm)
    header_box_h_mm = header_height_mm - header_shrink_top_mm
    _draw_rect(
        pdf,
        page_height_mm=config.page_config.height_mm,
        x_mm=header_box_x_mm,
        y_mm=header_box_y_mm,
        width_mm=header_box_w_mm,
        height_mm=header_box_h_mm,
        label="",
    )
    _draw_header_fields(
        pdf,
        page_height_mm=config.page_config.height_mm,
        x_mm=header_box_x_mm,
        y_mm=header_box_y_mm,
        width_mm=header_box_w_mm,
        height_mm=header_box_h_mm,
    )
    _draw_rect(
        pdf,
        page_height_mm=config.page_config.height_mm,
        x_mm=new_left_box_x_mm,
        y_mm=top_boxes_y_mm,
        width_mm=new_left_box_width_mm,
        height_mm=top_boxes_height_mm,
        label="DOCUMENTO",
    )
    _draw_document_type_omr(
        pdf,
        page_height_mm=config.page_config.height_mm,
        box_x_mm=new_left_box_x_mm,
        box_y_mm=top_boxes_y_mm,
        box_width_mm=new_left_box_width_mm,
        box_height_mm=top_boxes_height_mm,
    )
    _draw_rect(
        pdf,
        page_height_mm=config.page_config.height_mm,
        x_mm=student_box_x_mm,
        y_mm=top_boxes_y_mm,
        width_mm=student_box_width_mm,
        height_mm=top_boxes_height_mm,
        label="NUMERO DE IDENTIDAD",
    )
    _draw_id_bubble_grid(
        pdf,
        page_height_mm=config.page_config.height_mm,
        box_x_mm=student_box_x_mm,
        box_y_mm=top_boxes_y_mm,
        box_width_mm=student_box_width_mm,
        box_height_mm=top_boxes_height_mm,
        start_from_left_mm=id_grid_left_padding_mm,
    )
    _draw_rect(
        pdf,
        page_height_mm=config.page_config.height_mm,
        x_mm=exam_box_x_mm,
        y_mm=top_boxes_y_mm,
        width_mm=exam_box_width_mm,
        height_mm=top_boxes_height_mm,
        label="IDENTIFICACION EXAMEN",
    )
    id_grid_height_mm = 4.0 + (10 - 1) * 8.0
    id_origin_y_mm = top_boxes_y_mm + (top_boxes_height_mm - id_grid_height_mm) / 2.0
    right_cols, right_rows = _draw_right_bubble_grid(
        pdf,
        page_height_mm=config.page_config.height_mm,
        box_x_mm=exam_box_x_mm,
        box_y_mm=top_boxes_y_mm,
        box_width_mm=exam_box_width_mm,
        box_height_mm=top_boxes_height_mm,
        left_padding_mm=right_grid_left_padding_mm,
        aligned_origin_y_mm=id_origin_y_mm,
        forced_cols=4,
        forced_rows=10,
    )
    _draw_rect(
        pdf,
        page_height_mm=config.page_config.height_mm,
        x_mm=bottom_box_x_mm,
        y_mm=bottom_box_y_mm,
        width_mm=bottom_box_width_mm,
        height_mm=bottom_box_height_mm,
        label="RESPUESTAS",
    )
    _draw_answers_grid(
        pdf,
        page_height_mm=config.page_config.height_mm,
        box_x_mm=bottom_box_x_mm,
        box_y_mm=bottom_box_y_mm,
        box_width_mm=bottom_box_width_mm,
        box_height_mm=bottom_box_height_mm,
        rows=10,
        cols=4,
    )

    pdf.showPage()
    pdf.save()
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate wireframe PDF (Aruco + rectangles only)")
    parser.add_argument(
        "--config",
        default="config/template.base.json",
        help="Path to template config JSON (used for page + aruco geometry)",
    )
    parser.add_argument(
        "--output",
        default="data/output/template_wireframe_layout_v1.pdf",
        help="Output PDF path",
    )
    parser.add_argument("--header-height-mm", type=float, default=20.0)
    parser.add_argument("--header-to-top-gap-mm", type=float, default=10.0)
    parser.add_argument("--top-left-width-mm", type=float, default=92.0)
    parser.add_argument("--top-boxes-height-mm", type=float, default=88.0)
    parser.add_argument("--top-boxes-gap-mm", type=float, default=10.0)
    parser.add_argument("--top-to-bottom-gap-mm", type=float, default=10.0)
    parser.add_argument("--top-left-expand-left-mm", type=float, default=10.0)
    parser.add_argument("--id-grid-left-padding-mm", type=float, default=5.0)
    parser.add_argument("--top-right-expand-right-mm", type=float, default=10.0)
    parser.add_argument("--right-grid-left-padding-mm", type=float, default=5.0)
    parser.add_argument("--bottom-expand-left-mm", type=float, default=10.0)
    parser.add_argument("--bottom-expand-right-mm", type=float, default=10.0)
    parser.add_argument("--bottom-to-lower-markers-gap-mm", type=float, default=5.0)
    args = parser.parse_args()

    out = generate_wireframe_pdf(
        config_path=Path(args.config),
        output_path=Path(args.output),
        header_height_mm=args.header_height_mm,
        header_to_top_boxes_gap_mm=args.header_to_top_gap_mm,
        top_left_box_width_mm=args.top_left_width_mm,
        top_boxes_height_mm=args.top_boxes_height_mm,
        top_boxes_gap_mm=args.top_boxes_gap_mm,
        top_boxes_to_bottom_gap_mm=args.top_to_bottom_gap_mm,
        top_left_expand_left_mm=args.top_left_expand_left_mm,
        id_grid_left_padding_mm=args.id_grid_left_padding_mm,
        top_right_expand_right_mm=args.top_right_expand_right_mm,
        right_grid_left_padding_mm=args.right_grid_left_padding_mm,
        bottom_expand_left_mm=args.bottom_expand_left_mm,
        bottom_expand_right_mm=args.bottom_expand_right_mm,
        bottom_to_lower_markers_gap_mm=args.bottom_to_lower_markers_gap_mm,
    )
    print(f"Wireframe PDF: {out}")


if __name__ == "__main__":
    main()
