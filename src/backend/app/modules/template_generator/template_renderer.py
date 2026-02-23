from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.modules.template_generator.contracts import TemplateLayout

PRINTABLE_AREA_COLOR = Color(0.78, 0.78, 0.78)


def render_template_pdf(layout: TemplateLayout, output_path: str | Path) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    page_width_pt = layout.page.width_mm * mm
    page_height_pt = layout.page.height_mm * mm

    pdf = canvas.Canvas(str(out_path), pagesize=(page_width_pt, page_height_pt))
    pdf.setTitle(f"Template {layout.template_id} v{layout.version}")

    _draw_printable_area(pdf, layout)
    _draw_block(pdf, layout)
    _draw_markers(pdf, layout)
    _draw_bubbles(pdf, layout)
    _draw_question_numbers(pdf, layout)

    pdf.showPage()
    pdf.save()
    return out_path


def _draw_printable_area(pdf: canvas.Canvas, layout: TemplateLayout) -> None:
    pdf.setStrokeColor(PRINTABLE_AREA_COLOR)
    pdf.setLineWidth(0.6)
    pdf.rect(
        layout.printable_area.x_mm * mm,
        _invert_y(
            layout.page.height_mm,
            layout.printable_area.y_mm + layout.printable_area.height_mm,
        )
        * mm,
        layout.printable_area.width_mm * mm,
        layout.printable_area.height_mm * mm,
    )
    pdf.setStrokeColorRGB(0, 0, 0)


def _draw_block(pdf: canvas.Canvas, layout: TemplateLayout) -> None:
    pdf.setLineWidth(1)
    pdf.rect(
        layout.block.x_mm * mm,
        _invert_y(layout.page.height_mm, layout.block.y_mm + layout.block.height_mm) * mm,
        layout.block.width_mm * mm,
        layout.block.height_mm * mm,
    )


def _draw_markers(pdf: canvas.Canvas, layout: TemplateLayout) -> None:
    pdf.setLineWidth(1)
    for marker in layout.aruco_markers:
        x = marker.center_x_mm - (marker.size_mm / 2)
        y = marker.center_y_mm - (marker.size_mm / 2)
        pdf.rect(
            x * mm,
            _invert_y(layout.page.height_mm, y + marker.size_mm) * mm,
            marker.size_mm * mm,
            marker.size_mm * mm,
        )
        pdf.setFont("Helvetica", 7)
        pdf.drawString(
            (x + 1.2) * mm,
            _invert_y(layout.page.height_mm, y + 2.5) * mm,
            f"A{marker.marker_id}",
        )


def _draw_bubbles(pdf: canvas.Canvas, layout: TemplateLayout) -> None:
    pdf.setLineWidth(0.7)
    for bubble in layout.bubbles:
        pdf.circle(
            bubble.center_x_mm * mm,
            _invert_y(layout.page.height_mm, bubble.center_y_mm) * mm,
            bubble.radius_mm * mm,
            stroke=1,
            fill=0,
        )
        _draw_bubble_label(pdf, layout, bubble)


def _draw_bubble_label(pdf: canvas.Canvas, layout: TemplateLayout, bubble) -> None:
    style = layout.bubble_label_style
    gray = style.gray_level
    pdf.setFillColor(Color(gray, gray, gray))
    pdf.setFont(style.font_name, style.font_size_pt)
    text_width = pdf.stringWidth(bubble.label, style.font_name, style.font_size_pt)
    text_x = (bubble.center_x_mm * mm) - (text_width / 2.0)
    text_y = _invert_y(layout.page.height_mm, bubble.center_y_mm) * mm - (
        style.font_size_pt * 0.35
    )
    pdf.drawString(text_x, text_y, bubble.label)
    pdf.setFillColorRGB(0, 0, 0)


def _draw_question_numbers(pdf: canvas.Canvas, layout: TemplateLayout) -> None:
    style = layout.question_number_style
    if not style.enabled:
        return
    gray = style.gray_level
    pdf.setFillColor(Color(gray, gray, gray))
    pdf.setFont(style.font_name, style.font_size_pt)
    for item in layout.question_numbers:
        value = str(item.question_number)
        text_width = pdf.stringWidth(value, style.font_name, style.font_size_pt)
        text_x = (item.center_x_mm * mm) - (text_width / 2.0)
        text_y = _invert_y(layout.page.height_mm, item.center_y_mm) * mm - (
            style.font_size_pt * 0.35
        )
        pdf.drawString(text_x, text_y, value)
    pdf.setFillColorRGB(0, 0, 0)


def _invert_y(page_height_mm: float, y_mm: float) -> float:
    return page_height_mm - y_mm
