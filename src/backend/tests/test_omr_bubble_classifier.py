from __future__ import annotations

import numpy as np
import pytest

from app.modules.omr_reader.bubble_classifier import classify_bubbles
from app.modules.omr_reader.errors import InvalidMetadataError


def _base_metadata() -> dict:
    return {
        "template_id": "template_test",
        "version": "v1",
        "bubbles": [
            {
                "bubble_id": "G01_00_00",
                "group_id": "G01",
                "row": 0,
                "col": 0,
                "label": "A",
                "center_x_mm": 10.0,
                "center_y_mm": 10.0,
                "radius_mm": 2.5,
            },
            {
                "bubble_id": "G01_00_01",
                "group_id": "G01",
                "row": 0,
                "col": 1,
                "label": "B",
                "center_x_mm": 30.0,
                "center_y_mm": 10.0,
                "radius_mm": 2.5,
            },
        ],
    }


def test_classify_bubbles_marked_and_unmarked() -> None:
    image = np.full((300, 400, 3), 255, dtype=np.uint8)

    # Burbuja 1 marcada (disco negro en centro esperado).
    rr, cc = np.ogrid[:300, :400]
    mask_marked = (cc - 100) ** 2 + (rr - 100) ** 2 <= 20**2
    image[mask_marked] = 0

    metadata = _base_metadata()
    results = classify_bubbles(
        aligned_image=image,
        metadata=metadata,
        px_per_mm=10.0,
        marked_threshold=0.33,
        unmarked_threshold=0.18,
    )

    by_id = {item.bubble_id: item for item in results}
    assert by_id["G01_00_00"].state == "marcada"
    assert by_id["G01_00_01"].state == "no_marcada"


def test_classify_bubbles_ambiguous_state() -> None:
    image = np.full((300, 400, 3), 255, dtype=np.uint8)
    rr, cc = np.ogrid[:300, :400]

    # Semilleno controlado para forzar ratio intermedio (ambigua).
    mask = (cc - 100) ** 2 + (rr - 100) ** 2 <= 20**2
    half = (cc >= 100)
    image[mask & half] = 0

    metadata = {
        "template_id": "template_test",
        "version": "v1",
        "bubbles": [
            {
                "bubble_id": "G01_00_00",
                "group_id": "G01",
                "row": 0,
                "col": 0,
                "label": "A",
                "center_x_mm": 10.0,
                "center_y_mm": 10.0,
                "radius_mm": 2.5,
            }
        ],
    }

    results = classify_bubbles(
        aligned_image=image,
        metadata=metadata,
        px_per_mm=10.0,
        marked_threshold=0.70,
        unmarked_threshold=0.30,
    )

    assert results[0].state == "ambigua"


def test_classify_bubbles_fails_with_invalid_metadata() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    metadata = {"template_id": "t", "version": "v1", "bubbles": [{}]}

    with pytest.raises(InvalidMetadataError, match="bubble metadata missing keys"):
        classify_bubbles(aligned_image=image, metadata=metadata, px_per_mm=10.0)
