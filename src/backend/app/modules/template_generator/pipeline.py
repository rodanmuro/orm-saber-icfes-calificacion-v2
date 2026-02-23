from __future__ import annotations

from pathlib import Path

from app.modules.template_generator.config_loader import load_template_config
from app.modules.template_generator.layout_engine import build_template_layout
from app.modules.template_generator.metadata_exporter import export_layout_metadata
from app.modules.template_generator.template_renderer import render_template_pdf


def generate_template_artifacts(
    *,
    config_path: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    config = load_template_config(config_path)
    layout = build_template_layout(config)

    out_dir = Path(output_dir)
    pdf_path = out_dir / f"{layout.template_id}_{layout.version}.pdf"
    json_path = out_dir / f"{layout.template_id}_{layout.version}.json"

    render_template_pdf(layout, pdf_path)
    export_layout_metadata(layout, json_path)

    return pdf_path, json_path
