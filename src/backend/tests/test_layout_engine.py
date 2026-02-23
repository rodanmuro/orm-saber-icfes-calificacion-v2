from __future__ import annotations

import pytest

from app.modules.template_generator.contracts import TemplateConfig
from app.modules.template_generator.layout_engine import build_template_layout


def test_layout_engine_returns_expected_counts(base_config_dict: dict) -> None:
    config = TemplateConfig.model_validate(base_config_dict)

    layout = build_template_layout(config)

    assert len(layout.aruco_markers) == 4
    assert len(layout.bubbles) == 40
    assert layout.printable_area.width_mm > 0


def test_layout_engine_rejects_block_outside_printable_area(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["block_config"] = dict(payload["block_config"])
    payload["block_config"]["x_mm"] = 1.0

    config = TemplateConfig.model_validate(payload)

    with pytest.raises(ValueError, match="outside printable area"):
        build_template_layout(config)
