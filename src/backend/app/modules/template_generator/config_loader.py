from __future__ import annotations

import json
from pathlib import Path

from app.modules.template_generator.contracts import TemplateConfig


def load_template_config(config_path: str | Path) -> TemplateConfig:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return TemplateConfig.model_validate(payload)
