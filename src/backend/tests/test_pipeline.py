from __future__ import annotations

import json
from pathlib import Path

from app.modules.template_generator.pipeline import generate_template_artifacts


def test_pipeline_generates_pdf_and_json(base_config_json: Path, tmp_path: Path) -> None:
    pdf_path, json_path = generate_template_artifacts(
        config_path=base_config_json,
        output_dir=tmp_path,
    )

    assert pdf_path.exists()
    assert json_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["template_id"] == "template_test"
    assert payload["version"] == "v1"
    assert len(payload["bubbles"]) == 40
