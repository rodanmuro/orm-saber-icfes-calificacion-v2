from __future__ import annotations

from pathlib import Path

import pytest

from app.modules.template_generator.config_loader import load_template_config


def test_load_json_config_success(base_config_json: Path) -> None:
    config = load_template_config(base_config_json)
    assert config.output_config.template_id == "template_test"


def test_load_yaml_config_success(base_config_yaml: Path) -> None:
    config = load_template_config(base_config_yaml)
    assert config.output_config.template_id == "template_test_yaml"


def test_load_invalid_extension_raises(tmp_path: Path, base_config_json: Path) -> None:
    invalid_path = tmp_path / "template.invalid.txt"
    invalid_path.write_text(base_config_json.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported config extension"):
        load_template_config(invalid_path)


def test_load_yaml_root_not_mapping_raises(tmp_path: Path) -> None:
    yaml_path = tmp_path / "invalid.yaml"
    yaml_path.write_text("- item1\n- item2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="YAML config must be a mapping"):
        load_template_config(yaml_path)
