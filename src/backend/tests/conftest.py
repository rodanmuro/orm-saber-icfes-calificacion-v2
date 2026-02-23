from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def base_config_dict() -> dict:
    return {
        "page_config": {
            "width_mm": 215.9,
            "height_mm": 279.4,
            "margin_top_mm": 10.0,
            "margin_right_mm": 10.0,
            "margin_bottom_mm": 10.0,
            "margin_left_mm": 10.0,
        },
        "aruco_config": {
            "dictionary_name": "DICT_4X4_50",
            "marker_size_mm": 12.0,
            "corner_inset_mm": 10.0,
            "ids": [0, 1, 2, 3],
        },
        "block_config": {
            "x_mm": 30.0,
            "y_mm": 45.0,
            "width_mm": 155.0,
            "height_mm": 190.0,
        },
        "bubble_config": {
            "groups": [
                {
                    "group_id": "G01",
                    "rows": 10,
                    "cols": 4,
                    "radius_mm": 2.5,
                    "spacing_x_mm": 10.0,
                    "spacing_y_mm": 10.0,
                    "offset_x_mm": 12.0,
                    "offset_y_mm": 15.0,
                }
            ]
        },
        "output_config": {
            "template_id": "template_test",
            "version": "v1",
        },
    }


@pytest.fixture
def base_config_json(tmp_path: Path, base_config_dict: dict) -> Path:
    path = tmp_path / "template.test.json"
    path.write_text(json.dumps(base_config_dict), encoding="utf-8")
    return path


@pytest.fixture
def base_config_yaml(tmp_path: Path) -> Path:
    path = tmp_path / "template.test.yaml"
    path.write_text(
        """
page_config:
  width_mm: 215.9
  height_mm: 279.4
  margin_top_mm: 10.0
  margin_right_mm: 10.0
  margin_bottom_mm: 10.0
  margin_left_mm: 10.0
aruco_config:
  dictionary_name: DICT_4X4_50
  marker_size_mm: 12.0
  corner_inset_mm: 10.0
  ids: [0, 1, 2, 3]
block_config:
  x_mm: 30.0
  y_mm: 45.0
  width_mm: 155.0
  height_mm: 190.0
bubble_config:
  groups:
    - group_id: G01
      rows: 10
      cols: 4
      radius_mm: 2.5
      spacing_x_mm: 10.0
      spacing_y_mm: 10.0
      offset_x_mm: 12.0
      offset_y_mm: 15.0
output_config:
  template_id: template_test_yaml
  version: v1
""".strip(),
        encoding="utf-8",
    )
    return path
