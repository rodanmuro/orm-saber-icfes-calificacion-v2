from __future__ import annotations

import json
from pathlib import Path

from app.modules.template_generator.contracts import TemplateLayout


def export_layout_metadata(layout: TemplateLayout, output_path: str | Path) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as file:
        json.dump(layout.model_dump(mode="json"), file, indent=2)
    return out_path
