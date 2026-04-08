from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import matplotlib
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Emu, Inches, Pt, RGBColor

from app.db.models import Exam, ExamVersion, ExamVersionItem, Item

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Tamaño carta: 8.5" x 11"
PAGE_WIDTH_IN = 8.5
PAGE_HEIGHT_IN = 11.0
MARGIN_IN = 0.5
GUTTER_IN = 0.3
CONTENT_WIDTH_IN = PAGE_WIDTH_IN - 2 * MARGIN_IN
COLUMN_WIDTH_IN = (CONTENT_WIDTH_IN - GUTTER_IN) / 2  # ~3.6"

BACKEND_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = BACKEND_DIR / "data" / "input" / "item_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


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
    if clean.startswith("$") and clean.endswith("$") and len(clean) >= 2:
        clean = clean[1:-1].strip()
    if not clean:
        return None

    output_path = ASSETS_DIR / f"eq_{uuid4().hex}.png"
    try:
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_alpha(0)
        text = fig.text(0, 0, f"${clean}$", fontsize=10)
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


def _set_page_size_letter(doc: Document) -> None:
    """Configura tamaño carta y dos columnas en el documento Word."""
    section = doc.sections[0]
    section.page_width = Emu(int(PAGE_WIDTH_IN * 914400))
    section.page_height = Emu(int(PAGE_HEIGHT_IN * 914400))
    section.left_margin = Emu(int(MARGIN_IN * 914400))
    section.right_margin = Emu(int(MARGIN_IN * 914400))
    section.top_margin = Emu(int(MARGIN_IN * 914400))
    section.bottom_margin = Emu(int(MARGIN_IN * 914400))

    # Dos columnas con gutter de 0.3"
    sectPr = section._sectPr
    # Eliminar <w:cols> previo si existe
    for existing in sectPr.findall(qn("w:cols")):
        sectPr.remove(existing)
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), "2")
    cols.set(qn("w:space"), str(int(0.3 * 1440)))  # 1440 twips por pulgada
    sectPr.append(cols)


def _add_heading(doc: Document, text: str, level: int = 2) -> None:
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT


def _add_table_node(doc: Document, node: dict[str, Any]) -> None:
    rows_nodes = [r for r in (node.get("content") or []) if isinstance(r, dict) and r.get("type") == "tableRow"]
    if not rows_nodes:
        return

    matrix: list[list[str]] = []
    for row_node in rows_nodes:
        cells = [c for c in (row_node.get("content") or []) if isinstance(c, dict)]
        row_texts: list[str] = []
        for cell in cells:
            parts: list[str] = []
            _collect_text(cell, parts)
            row_texts.append(" ".join(p for p in parts if p).strip())
        if row_texts:
            matrix.append(row_texts)

    if not matrix:
        return

    num_cols = max(len(r) for r in matrix)
    if num_cols == 0:
        return

    table = doc.add_table(rows=len(matrix), cols=num_cols)
    table.style = "Table Grid"
    for r_idx, row_data in enumerate(matrix):
        for c_idx in range(num_cols):
            cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
            cell = table.cell(r_idx, c_idx)
            cell.text = cell_text
            if r_idx == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
                    run.font.size = Pt(8)
            else:
                for run in cell.paragraphs[0].runs:
                    run.font.size = Pt(8)


def _collect_text(node: Any, parts: list[str]) -> None:
    if not isinstance(node, dict):
        return
    node_type = node.get("type")
    if node_type == "text":
        text = node.get("text")
        if text:
            parts.append(str(text))
        return
    if node_type == "hardBreak":
        parts.append("\n")
        return
    content = node.get("content")
    if isinstance(content, list):
        for child in content:
            _collect_text(child, parts)


def _render_doc_node_to_paragraph(
    doc: Document,
    node: Any,
    prefix: str = "",
    image_max_width: float = COLUMN_WIDTH_IN - 0.1,
) -> None:
    """Renderiza un nodo Tiptap al documento Word."""
    if not isinstance(node, dict):
        return

    node_type = node.get("type")

    if node_type == "doc":
        for child in (node.get("content") or []):
            _render_doc_node_to_paragraph(doc, child, prefix=prefix, image_max_width=image_max_width)
        return

    if node_type == "paragraph":
        text_parts: list[str] = []
        image_paths: list[Path] = []
        math_paths: list[Path] = []

        for child in (node.get("content") or []):
            child_type = child.get("type") if isinstance(child, dict) else None
            if child_type == "text":
                txt = child.get("text")
                if txt:
                    text_parts.append(str(txt))
            elif child_type == "hardBreak":
                text_parts.append("\n")
            elif child_type == "image":
                src = (child.get("attrs") or {}).get("src", "")
                path = _asset_path_from_src(str(src))
                if path:
                    image_paths.append(path)
            elif child_type == "mathInline":
                latex = (child.get("attrs") or {}).get("latex", "")
                if latex:
                    eq_path = _render_latex_to_png(str(latex))
                    if eq_path:
                        math_paths.append(eq_path)

        full_text = (prefix + "".join(text_parts)).strip()
        if full_text:
            p = doc.add_paragraph()
            run = p.add_run(full_text)
            run.font.size = Pt(9)
        for path in image_paths:
            p = doc.add_paragraph()
            run = p.add_run()
            run.add_picture(str(path), width=Inches(min(image_max_width, 3.5)))
        for path in math_paths:
            p = doc.add_paragraph()
            run = p.add_run()
            run.add_picture(str(path), width=Inches(min(1.5, image_max_width)))
        return

    if node_type == "image":
        src = (node.get("attrs") or {}).get("src", "")
        path = _asset_path_from_src(str(src))
        if path:
            p = doc.add_paragraph()
            run = p.add_run()
            run.add_picture(str(path), width=Inches(min(image_max_width, 3.5)))
        return

    if node_type == "mathInline":
        latex = (node.get("attrs") or {}).get("latex", "")
        if latex:
            eq_path = _render_latex_to_png(str(latex))
            if eq_path:
                p = doc.add_paragraph()
                run = p.add_run()
                run.add_picture(str(eq_path), width=Inches(min(1.5, image_max_width)))
        return

    if node_type == "table":
        _add_table_node(doc, node)
        return

    # Listas y otros nodos con content
    for child in (node.get("content") or []):
        _render_doc_node_to_paragraph(doc, child, prefix=prefix, image_max_width=image_max_width)


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


def build_exam_version_docx(
    *,
    exam: Exam,
    version: ExamVersion,
    version_items: list[ExamVersionItem],
    items_by_id: dict[int, Item],
) -> bytes:
    doc = Document()
    _set_page_size_letter(doc)

    # Encabezado del examen
    title_p = doc.add_heading(f"Cuadernillo: {exam.title}", level=1)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta = doc.add_paragraph()
    meta.add_run(f"Código de examen: {exam.exam_code}   |   Versión: {version.version_code}").bold = True
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()  # espaciado

    for row in version_items:
        item = items_by_id.get(row.item_id)
        if item is None:
            continue

        # Título de la pregunta
        q_heading = doc.add_paragraph()
        q_run = q_heading.add_run(f"Pregunta {row.question_number}")
        q_run.bold = True
        q_run.font.size = Pt(10)
        q_run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)

        # Enunciado
        statement_doc = _parse_storage_doc(item.statement)
        _render_doc_node_to_paragraph(doc, statement_doc, image_max_width=COLUMN_WIDTH_IN - 0.1)

        # Opciones A/B/C/D
        mapped_options = _mapped_options_for_version(item, row.option_map_json)
        for label in ("A", "B", "C", "D"):
            option_doc = _parse_storage_doc(mapped_options.get(label, ""))
            _render_doc_node_to_paragraph(
                doc, option_doc, prefix=f"{label}. ", image_max_width=COLUMN_WIDTH_IN - 0.3
            )

        doc.add_paragraph()  # separador entre preguntas

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
