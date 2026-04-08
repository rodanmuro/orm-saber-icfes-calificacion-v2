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


def _table_as_lines(node: dict[str, Any]) -> list[str]:
    rows = node.get("content")
    if not isinstance(rows, list):
        return []

    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            continue
        cells = row.get("content")
        if not isinstance(cells, list):
            continue
        values: list[str] = []
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            cell_text_parts: list[str] = []
            paragraphs = cell.get("content")
            if isinstance(paragraphs, list):
                for paragraph in paragraphs:
                    if not isinstance(paragraph, dict):
                        continue
                    cell_text_parts.extend(_node_to_text_parts(paragraph, [], []))
            values.append(" ".join(part for part in cell_text_parts if part).strip())
        out.append(" | ".join(values))
    return out


def _table_as_matrix(node: dict[str, Any]) -> list[list[str]]:
    rows = node.get("content")
    if not isinstance(rows, list):
        return []

    matrix: list[list[str]] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            continue
        cells = row.get("content")
        if not isinstance(cells, list):
            continue
        values: list[str] = []
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            cell_text_parts: list[str] = []
            paragraphs = cell.get("content")
            if isinstance(paragraphs, list):
                for paragraph in paragraphs:
                    if not isinstance(paragraph, dict):
                        continue
                    cell_text_parts.extend(_node_to_text_parts(paragraph, [], [], []))
            values.append(" ".join(part for part in cell_text_parts if part).strip())
        if values:
            matrix.append(values)
    if not matrix:
        return []

    max_cols = max(len(row) for row in matrix)
    if max_cols <= 0:
        return []

    normalized: list[list[str]] = []
    for row in matrix:
        if len(row) < max_cols:
            normalized.append(row + [""] * (max_cols - len(row)))
        else:
            normalized.append(row[:max_cols])
    return normalized


def _asset_path_from_src(src: str) -> Path | None:
    src = src.strip()
    if not src:
        return None
    backend_root = Path(__file__).resolve().parents[3]
    assets_root = backend_root / "data" / "input"

    if src.startswith("/assets/"):
        rel = src.removeprefix("/assets/").strip("/")
        path = assets_root / rel
        return path if path.exists() else None

    marker = "/assets/"
    idx = src.find(marker)
    if idx >= 0:
        rel = src[idx + len(marker) :].strip("/")
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

    filename = f"eq_{uuid4().hex}.png"
    output_path = ASSETS_DIR / filename
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
        fig.savefig(
            output_path,
            dpi=dpi,
            transparent=True,
            format="png",
            bbox_inches="tight",
            pad_inches=0.01,
        )
        plt.close(fig)
        return output_path if output_path.exists() else None
    except Exception:  # noqa: BLE001
        plt.close("all")
        return None


def _node_to_text_parts(
    node: Any,
    image_paths: list[Path],
    math_paths: list[Path],
    table_matrices: list[list[list[str]]],
) -> list[str]:
    if not isinstance(node, dict):
        return []
    node_type = node.get("type")

    if node_type == "text":
        text = node.get("text")
        return [str(text)] if text is not None else []
    if node_type == "mathInline":
        latex = (node.get("attrs") or {}).get("latex", "")
        if latex:
            eq_path = _render_latex_to_png(str(latex))
            if eq_path is not None:
                math_paths.append(eq_path)
            return []
        return []
    if node_type == "hardBreak":
        return ["\n"]
    if node_type == "image":
        src = (node.get("attrs") or {}).get("src", "")
        if isinstance(src, str):
            path = _asset_path_from_src(src)
            if path is not None:
                image_paths.append(path)
        return []
    if node_type == "table":
        matrix = _table_as_matrix(node)
        if matrix:
            table_matrices.append(matrix)
        return []

    parts: list[str] = []
    content = node.get("content")
    if isinstance(content, list):
        for child in content:
            parts.extend(_node_to_text_parts(child, image_paths, math_paths, table_matrices))
    if node_type in {"paragraph", "tableRow", "bulletList", "orderedList"} and parts:
        parts.append("\n")
    return parts


def _doc_to_text_and_images(value: Any) -> tuple[str, list[Path], list[Path], list[list[list[str]]]]:
    doc = _parse_storage_doc(value)
    image_paths: list[Path] = []
    math_paths: list[Path] = []
    table_matrices: list[list[list[str]]] = []
    parts = _node_to_text_parts(doc, image_paths, math_paths, table_matrices)
    text = "".join(parts).strip()
    return text, image_paths, math_paths, table_matrices


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
        doc.leftMargin,
        doc.bottomMargin,
        column_width,
        frame_height,
        id="left-col",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    right_frame = Frame(
        doc.leftMargin + column_width + gutter,
        doc.bottomMargin,
        column_width,
        frame_height,
        id="right-col",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="two-col", frames=[left_frame, right_frame])])

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ExamTitle",
        parent=styles["Heading2"],
        fontSize=12,
        leading=14,
        spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "QuestionHeading",
        parent=styles["Heading4"],
        fontSize=9,
        leading=11,
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "ExamBody",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=10.2,
        spaceAfter=1.2,
    )

    story: list[Any] = [
        Paragraph(f"Cuadernillo: {exam.title}", title_style),
        Paragraph(f"Codigo de examen: {exam.exam_code}", body_style),
        Paragraph(f"Version: {version.version_code}", body_style),
        Spacer(1, 4),
    ]

    for row in version_items:
        item = items_by_id.get(row.item_id)
        if item is None:
            continue

        statement_text, statement_images, statement_math_images, statement_tables = _doc_to_text_and_images(
            item.statement
        )
        question_title = f"Pregunta {row.question_number}"
        story.append(Paragraph(question_title, heading_style))
        if statement_text:
            story.append(Paragraph(escape(statement_text).replace("\n", "<br/>"), body_style))
        for matrix in statement_tables:
            try:
                cols = max(len(r) for r in matrix) if matrix else 1
                col_width = (column_width - 2 * mm) / max(cols, 1)
                t = Table(matrix, colWidths=[col_width] * cols, repeatRows=1)
                t.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 7),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                            ("TOPPADDING", (0, 0), (-1, -1), 2),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f7")),
                        ]
                    )
                )
                story.append(t)
                story.append(Spacer(1, 1.4))
            except Exception:  # noqa: BLE001
                for matrix_row in matrix:
                    story.append(Paragraph(escape(" | ".join(matrix_row)), body_style))
        for path in statement_images:
            img = Image(str(path))
            img._restrictSize(column_width - 4 * mm, 42 * mm)
            story.append(img)
            story.append(Spacer(1, 1.5))
        for path in statement_math_images:
            img = Image(str(path))
            img._restrictSize(column_width - 22 * mm, 5.8 * mm)
            story.append(img)
            story.append(Spacer(1, 1.0))

        mapped_options = _mapped_options_for_version(item, row.option_map_json)
        for label in ("A", "B", "C", "D"):
            option_text, option_images, option_math_images, _ = _doc_to_text_and_images(
                mapped_options.get(label, "")
            )
            if option_text and not option_images and not option_math_images:
                # Caso comun: opcion textual compacta en una sola linea.
                safe_line = escape(f"{label}. {option_text}")
                story.append(Paragraph(safe_line.replace("\n", "<br/>"), body_style))
            else:
                # Mantener etiqueta visible cuando la opcion es visual/mixta.
                story.append(Paragraph(f"{label}.", body_style))
                if option_text:
                    safe_line = escape(option_text)
                    story.append(Paragraph(safe_line.replace("\n", "<br/>"), body_style))
            for path in option_images:
                img = Image(str(path))
                img._restrictSize(column_width - 14 * mm, 30 * mm)
                story.append(img)
                story.append(Spacer(1, 0.8))
            for path in option_math_images:
                img = Image(str(path))
                img._restrictSize(column_width - 36 * mm, 4.8 * mm)
                story.append(img)
                story.append(Spacer(1, 0.6))
        story.append(Spacer(1, 2.6))

    doc.build(story)
    return buffer.getvalue()
