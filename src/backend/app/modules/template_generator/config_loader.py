from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from app.modules.template_generator.contracts import TemplateConfig


SUPPORTED_CONFIG_EXTENSIONS = {".json", ".yaml", ".yml"}


def load_template_config(config_path: str | Path) -> TemplateConfig:
    path = Path(config_path)
    payload = _read_config_payload(path)
    return TemplateConfig.model_validate(payload)


def _read_config_payload(path: Path) -> dict[str, Any]:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_CONFIG_EXTENSIONS:
        raise ValueError(
            f"unsupported config extension '{extension}'. Use JSON or YAML"
        )

    with path.open("r", encoding="utf-8") as file:
        if extension == ".json":
            return json.load(file)
        data = yaml.safe_load(file)
        if not isinstance(data, dict):
            raise ValueError("YAML config must be a mapping at root level")
        return data
