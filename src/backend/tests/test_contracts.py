from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.template_generator.contracts import TemplateConfig


def test_template_config_rejects_duplicate_aruco_ids(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["aruco_config"] = dict(payload["aruco_config"])
    payload["aruco_config"]["ids"] = [1, 1, 2, 3]

    with pytest.raises(ValidationError):
        TemplateConfig.model_validate(payload)


def test_template_config_rejects_invalid_margins(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["page_config"] = dict(payload["page_config"])
    payload["page_config"]["margin_left_mm"] = 200.0
    payload["page_config"]["margin_right_mm"] = 20.0

    with pytest.raises(ValidationError):
        TemplateConfig.model_validate(payload)


def test_template_config_rejects_unsupported_aruco_dictionary(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["aruco_config"] = dict(payload["aruco_config"])
    payload["aruco_config"]["dictionary_name"] = "DICT_UNKNOWN"

    with pytest.raises(ValidationError):
        TemplateConfig.model_validate(payload)


def test_template_config_rejects_aruco_id_out_of_range(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["aruco_config"] = dict(payload["aruco_config"])
    payload["aruco_config"]["dictionary_name"] = "DICT_4X4_50"
    payload["aruco_config"]["ids"] = [0, 1, 2, 50]

    with pytest.raises(ValidationError):
        TemplateConfig.model_validate(payload)
