from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.modules.template_generator.contracts import TemplateLayout


def render_template_pdf(layout: TemplateLayout, output_path: str | Path) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    page_width_pt = layout.page.width_mm * mm
    page_height_pt = layout.page.height_mm * mm

    pdf = canvas.Canvas(str(out_path), pagesize=(page_width_pt, page_height_pt))
    pdf.setTitle(f"Template {layout.template_id} v{layout.version}")

    _draw_block(pdf, layout)
    _draw_markers(pdf, layout)
    _draw_bubbles(pdf, layout)

    pdf.showPage()
    pdf.save()
    return out_path


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


def _invert_y(page_height_mm: float, y_mm: float) -> float:
    return page_height_mm - y_mm
