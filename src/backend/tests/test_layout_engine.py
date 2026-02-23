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
    assert layout.main_block_bbox == layout.block


def test_layout_engine_rejects_block_outside_printable_area(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["block_config"] = dict(payload["block_config"])
    payload["block_config"]["x_mm"] = 1.0

    config = TemplateConfig.model_validate(payload)

    with pytest.raises(ValueError, match="outside printable area"):
        build_template_layout(config)


def test_layout_engine_rejects_aruco_outside_printable_area(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["aruco_config"] = dict(payload["aruco_config"])
    payload["aruco_config"]["corner_inset_mm"] = 0.0
    payload["aruco_config"]["corner_offsets_mm"] = {
        "top_left": {"x_mm": 200.0, "y_mm": 0.0},
        "top_right": {"x_mm": 0.0, "y_mm": 0.0},
        "bottom_left": {"x_mm": 0.0, "y_mm": 0.0},
        "bottom_right": {"x_mm": 0.0, "y_mm": 0.0},
    }

    config = TemplateConfig.model_validate(payload)

    with pytest.raises(ValueError, match="outside printable area"):
        build_template_layout(config)


def test_layout_engine_rejects_aruco_overlapping_main_block(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["block_config"] = dict(payload["block_config"])
    payload["block_config"]["x_mm"] = 10.0
    payload["block_config"]["y_mm"] = 10.0
    payload["block_config"]["width_mm"] = 80.0
    payload["block_config"]["height_mm"] = 80.0

    config = TemplateConfig.model_validate(payload)

    with pytest.raises(ValueError, match="overlaps main block"):
        build_template_layout(config)
