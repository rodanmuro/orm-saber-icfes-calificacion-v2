from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4
from xml.sax.saxutils import escape

import matplotlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    Paragraph,
    PageTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.db.models import Exam, ExamVersion, ExamVersionItem, Item

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BACKEND_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = BACKEND_DIR / "data" / "input" / "item_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Altura objetivo para ecuaciones inline (puntos tipográficos)
MATH_INLINE_HEIGHT_PT = 9.0


def _parse_storage_doc(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return {"type": "doc", "content": []}
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        return {
            "type": "doc",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": value}]}],
        }
    return {"type": "doc", "content": []}


def _table_as_paragraph_matrix(
    node: dict[str, Any],
    column_width: float,
    cell_style: Any,
    header_style: Any,
) -> list[list[Any]]:
    """
    Construye una matriz de Paragraph para ReportLab Table.
    Soporta celdas con texto, mathInline e imágenes inline.
    """
    rows = node.get("content")
    if not isinstance(rows, list):
        return []

    matrix: list[list[Any]] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            continue
        cells = row.get("content")
        if not isinstance(cells, list):
            continue
        row_data: list[Any] = []
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            is_header = cell.get("type") == "tableHeader"
            style = header_style if is_header else cell_style
            markup = _build_inline_markup(cell, column_width)
            markup = markup.strip()
            while markup.endswith("<br/>"):
                markup = markup[:-5].strip()
            row_data.append(Paragraph(markup or " ", style))
        if row_data:
            matrix.append(row_data)

    if not matrix:
        return []

    max_cols = max(len(r) for r in matrix)
    if max_cols <= 0:
        return []

    for row in matrix:
        while len(row) < max_cols:
            row.append(Paragraph(" ", cell_style))

    return matrix


def _collect_plain_text(node: Any, parts: list[str]) -> None:
    """Extrae texto plano de un nodo Tiptap (usado para celdas de tabla)."""
    if not isinstance(node, dict):
        return
    if node.get("type") == "text":
        text = node.get("text")
        if text:
            parts.append(str(text))
        return
    if node.get("type") == "hardBreak":
        parts.append(" ")
        return
    for child in (node.get("content") or []):
        _collect_plain_text(child, parts)


def _asset_path_from_src(src: str) -> Path | None:
    src = src.strip()
    if not src:
        return None
    assets_root = BACKEND_DIR / "data" / "input"

    if src.startswith("/assets/"):
        rel = src.removeprefix("/assets/").strip("/")
        path = assets_root / rel
        return path if path.exists() else None

    marker = "/assets/"
    idx = src.find(marker)
    if idx >= 0:
        rel = src[idx + len(marker):].strip("/")
        path = assets_root / rel
        return path if path.exists() else None
    return None


def _render_latex_to_png(latex: str) -> Path | None:
    clean = str(latex or "").strip()
    if not clean:
        return None
    while clean.startswith("$") and clean.endswith("$") and len(clean) >= 2:
        clean = clean[1:-1].strip()
    if not clean:
        return None

    output_path = ASSETS_DIR / f"eq_{uuid4().hex}.png"
    try:
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_alpha(0)
        text = fig.text(0, 0, f"${clean}$", fontsize=9.5)
        fig.canvas.draw()
        bbox = text.get_window_extent(renderer=fig.canvas.get_renderer()).expanded(1.08, 1.25)
        dpi = 160
        width_in = max(bbox.width / dpi, 0.2)
        height_in = max(bbox.height / dpi, 0.12)
        fig.set_size_inches(width_in, height_in)
        text.set_position((0.02, 0.04))
        fig.savefig(output_path, dpi=dpi, transparent=True, format="png",
                    bbox_inches="tight", pad_inches=0.01)
        plt.close(fig)
        return output_path if output_path.exists() else None
    except Exception:  # noqa: BLE001
        plt.close("all")
        return None


def _inline_img_tag(path: Path, target_h_pt: float, max_w_pt: float) -> str:
    """Genera un tag <img> inline para ReportLab Paragraph escalado a target_h_pt."""
    try:
        reader = ImageReader(str(path))
        iw, ih = reader.getSize()  # píxeles
        if ih <= 0:
            return ""
        scale = target_h_pt / ih
        dw = iw * scale
        # Si el ancho supera el máximo, reescalar por ancho
        if dw > max_w_pt:
            scale = max_w_pt / iw
            dw = max_w_pt
            dh = ih * scale
        else:
            dh = target_h_pt
        return f'<img src="{path}" width="{dw:.2f}" height="{dh:.2f}" valign="middle"/>'
    except Exception:  # noqa: BLE001
        return ""


def _build_inline_markup(node: Any, column_width_pt: float) -> str:
    """
    Convierte un nodo Tiptap a markup XML inline de ReportLab.
    Texto, ecuaciones mathInline e imágenes pequeñas quedan en la misma línea.
    """
    if not isinstance(node, dict):
        return ""
    node_type = node.get("type")

    if node_type == "text":
        text = node.get("text") or ""
        result = escape(str(text))
        marks = node.get("marks") or []
        for mark in reversed(marks):
            if not isinstance(mark, dict):
                continue
            mtype = mark.get("type")
            if mtype == "bold":
                result = f"<b>{result}</b>"
            elif mtype == "italic":
                result = f"<i>{result}</i>"
            elif mtype == "underline":
                result = f"<u>{result}</u>"
        return result

    if node_type == "hardBreak":
        return "<br/>"

    if node_type == "mathInline":
        latex = (node.get("attrs") or {}).get("latex", "")
        if latex:
            path = _render_latex_to_png(str(latex))
            if path:
                return _inline_img_tag(path, MATH_INLINE_HEIGHT_PT, column_width_pt - 4)
        return ""

    if node_type == "image":
        src = (node.get("attrs") or {}).get("src", "")
        path = _asset_path_from_src(str(src)) if isinstance(src, str) else None
        if path:
            # Imagen inline dentro de texto: altura máxima conservadora
            return _inline_img_tag(path, MATH_INLINE_HEIGHT_PT * 3, column_width_pt - 4)
        return ""

    # Nodos contenedor: paragraph, listItem, bulletList, etc.
    parts: list[str] = []
    for child in (node.get("content") or []):
        parts.append(_build_inline_markup(child, column_width_pt))
    markup = "".join(parts)
    if node_type in {"paragraph", "listItem"} and markup:
        markup += "<br/>"
    return markup


def _image_pixel_size(path: Path) -> tuple[int, int]:
    """Devuelve (ancho, alto) en píxeles de una imagen. (0, 0) si falla."""
    try:
        reader = ImageReader(str(path))
        iw, ih = reader.getSize()
        return int(iw), int(ih)
    except Exception:  # noqa: BLE001
        return 0, 0


def _is_pure_image_paragraph(node: dict[str, Any]) -> Path | None:
    """Si el párrafo contiene únicamente un nodo image, devuelve su path; si no, None."""
    content = node.get("content") or []
    if len(content) != 1:
        return None
    child = content[0]
    if not isinstance(child, dict) or child.get("type") != "image":
        return None
    src = (child.get("attrs") or {}).get("src", "")
    return _asset_path_from_src(str(src)) if isinstance(src, str) else None


def _merge_inline_image_paragraphs(nodes: list[Any]) -> list[Any]:
    """
    Pre-proceso del árbol de nodos Tiptap: si un párrafo que contiene únicamente
    una imagen pequeña (número, valor, fórmula corta) aparece inmediatamente después
    de un párrafo de texto, fusiona el nodo image dentro del párrafo anterior para
    que se renderice inline en lugar de como bloque separado.

    Umbral "pequeña": alto < 160 px  (figuras/gráficas suelen superar 200 px).
    """
    result: list[Any] = []
    for node in nodes:
        if not isinstance(node, dict) or node.get("type") != "paragraph":
            result.append(node)
            continue

        path = _is_pure_image_paragraph(node)
        if path is None:
            result.append(node)
            continue

        # Es un párrafo de imagen pura — ¿es pequeña?
        _iw, ih = _image_pixel_size(path)
        is_small = 0 < ih < 160

        if is_small and result:
            last = result[-1]
            if isinstance(last, dict) and last.get("type") == "paragraph":
                # Fusionar: añadir el nodo image al contenido del párrafo anterior
                merged_content = list(last.get("content") or []) + list(node.get("content") or [])
                result[-1] = {**last, "content": merged_content}
                continue

        result.append(node)
    return result


def _render_tiptap_doc(
    value: Any,
    column_width: float,
    body_style: ParagraphStyle,
    prefix_markup: str = "",
) -> list[Any]:
    """
    Convierte un doc Tiptap a lista de story items de ReportLab.

    - Tablas → Table flowable
    - Párrafos con sólo una imagen → Image flowable (usa ancho completo de columna)
    - Párrafos con texto/math/imagen mixta → Paragraph con markup inline
    """
    doc = _parse_storage_doc(value)
    items: list[Any] = []
    first_paragraph_done = False

    raw_nodes = doc.get("content") or []
    nodes = _merge_inline_image_paragraphs(raw_nodes)

    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = node.get("type")

        if node_type == "image":
            # Imagen a nivel de doc (no dentro de paragraph): siempre bloque
            src = (node.get("attrs") or {}).get("src", "")
            path = _asset_path_from_src(str(src)) if isinstance(src, str) else None
            if path:
                if not first_paragraph_done and prefix_markup:
                    items.append(Paragraph(prefix_markup.strip(), body_style))
                    first_paragraph_done = True
                img = Image(str(path))
                img._restrictSize(column_width - 4 * mm, 42 * mm)
                items.append(img)
                items.append(Spacer(1, 0))
            continue

        if node_type == "table":
            cell_style = ParagraphStyle(
                "TableCell", parent=body_style, fontSize=7, leading=9, spaceAfter=0,
            )
            header_style = ParagraphStyle(
                "TableHeader", parent=cell_style, fontName="Helvetica-Bold",
            )
            matrix = _table_as_paragraph_matrix(node, column_width, cell_style, header_style)
            if not matrix:
                continue
            try:
                cols = max(len(r) for r in matrix)
                col_w = (column_width - 2 * mm) / max(cols, 1)
                t = Table(matrix, colWidths=[col_w] * cols, repeatRows=1)
                t.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f7")),
                ]))
                items.append(t)
                items.append(Spacer(1, 0))
            except Exception:  # noqa: BLE001
                for matrix_row in matrix:
                    plain = " | ".join(
                        p.text if hasattr(p, "text") else str(p) for p in matrix_row
                    )
                    items.append(Paragraph(escape(plain), body_style))
            continue

        if node_type == "paragraph":
            pure_img_path = _is_pure_image_paragraph(node)
            if pure_img_path:
                # Imagen de bloque: usa el ancho completo de columna
                img = Image(str(pure_img_path))
                img._restrictSize(column_width - 4 * mm, 42 * mm)
                items.append(img)
                items.append(Spacer(1, 0))
                continue

        # Párrafo mixto u otro nodo contenedor → markup inline
        markup = _build_inline_markup(node, column_width)
        # Agregar prefijo (ej. "A. ") al primer párrafo del doc
        if not first_paragraph_done and prefix_markup:
            markup = prefix_markup + markup
        markup = markup.strip()
        while markup.endswith("<br/>"):
            markup = markup[:-5].strip()
        if markup:
            items.append(Paragraph(markup, body_style))
            first_paragraph_done = True

    # Si el doc estaba vacío pero hay prefijo, emitir el prefijo solo
    if not first_paragraph_done and prefix_markup.strip():
        items.append(Paragraph(prefix_markup.strip(), body_style))

    return items


def _mapped_options_for_version(item: Item, option_map: dict[str, str] | None) -> dict[str, Any]:
    options = item.options or {}
    if not option_map:
        return {k: options.get(k, "") for k in ("A", "B", "C", "D")}

    mapped: dict[str, Any] = {}
    for original_label, mapped_label in option_map.items():
        if mapped_label in {"A", "B", "C", "D"}:
            mapped[mapped_label] = options.get(original_label, "")
    for label in ("A", "B", "C", "D"):
        mapped.setdefault(label, options.get(label, ""))
    return mapped


def build_exam_version_pdf(
    *,
    exam: Exam,
    version: ExamVersion,
    version_items: list[ExamVersionItem],
    items_by_id: dict[int, Item],
) -> bytes:
    buffer = BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=f"Cuadernillo {exam.exam_code} {version.version_code}",
    )
    page_width, page_height = LETTER
    gutter = 6 * mm
    usable_width = page_width - doc.leftMargin - doc.rightMargin
    column_width = (usable_width - gutter) / 2.0
    frame_height = page_height - doc.topMargin - doc.bottomMargin
    left_frame = Frame(
        doc.leftMargin, doc.bottomMargin, column_width, frame_height,
        id="left-col", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    right_frame = Frame(
        doc.leftMargin + column_width + gutter, doc.bottomMargin, column_width, frame_height,
        id="right-col", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="two-col", frames=[left_frame, right_frame])])

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ExamTitle", parent=styles["Heading2"], fontSize=12, leading=14, spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "QuestionHeading", parent=styles["Heading4"], fontSize=9, leading=11, spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "ExamBody", parent=styles["BodyText"], fontSize=8.5, leading=10.2, spaceAfter=0,
    )

    story: list[Any] = [
        Paragraph(f"Cuadernillo: {exam.title}", title_style),
        Paragraph(f"Codigo de examen: {exam.exam_code}", body_style),
        Paragraph(f"Version: {version.version_code}", body_style),
        Spacer(1, 4),
    ]

    for version_row in version_items:
        item = items_by_id.get(version_row.item_id)
        if item is None:
            continue

        story.append(Paragraph(f"Pregunta {version_row.question_number}", heading_style))
        story.extend(_render_tiptap_doc(item.statement, column_width, body_style))

        mapped_options = _mapped_options_for_version(item, version_row.option_map_json)
        for label in ("A", "B", "C", "D"):
            story.extend(
                _render_tiptap_doc(
                    mapped_options.get(label, ""),
                    column_width,
                    body_style,
                    prefix_markup=f"<b>{escape(label)}.</b> ",
                )
            )
        story.append(Spacer(1, 2.6))

    doc.build(story)
    return buffer.getvalue()
