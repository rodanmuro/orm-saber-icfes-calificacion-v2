from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2

from app.modules.omr_reader.contracts import OMRReadImageContext
from app.modules.omr_reader.errors import (
    InputFileNotFoundError,
    InvalidImageError,
    InvalidMetadataError,
)

REQUIRED_READ_KEYS = {
    "template_id",
    "version",
    "question_items",
    "bubbles",
    "aruco_markers",
}


def load_local_read_input(*, image_path: str | Path, metadata_path: str | Path) -> OMRReadImageContext:
    image_file = Path(image_path)
    metadata_file = Path(metadata_path)

    _validate_file_exists(image_file, "image")
    _validate_file_exists(metadata_file, "metadata")

    image = cv2.imread(str(image_file), cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError(
            f"image file '{image_file}' could not be decoded. "
            "Use a valid JPG/PNG image path."
        )

    metadata = _load_metadata(metadata_file)
    _validate_read_metadata(metadata)

    return OMRReadImageContext(
        image_path=image_file,
        metadata_path=metadata_file,
        metadata=metadata,
        image=image,
    )


def _validate_file_exists(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise InputFileNotFoundError(f"{label} file not found: '{path}'")


def _load_metadata(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InvalidMetadataError(
            f"metadata file '{path}' is not valid JSON: {exc.msg}"
        ) from exc

    if not isinstance(payload, dict):
        raise InvalidMetadataError("metadata root must be a JSON object")

    return payload


def _validate_read_metadata(payload: dict[str, Any]) -> None:
    missing = REQUIRED_READ_KEYS - set(payload.keys())
    if missing:
        raise InvalidMetadataError(f"metadata missing required keys: {sorted(missing)}")

    if not isinstance(payload.get("aruco_markers"), list) or len(payload["aruco_markers"]) != 4:
        raise InvalidMetadataError("metadata 'aruco_markers' must contain exactly 4 items")

    if not isinstance(payload.get("bubbles"), list) or len(payload["bubbles"]) == 0:
        raise InvalidMetadataError("metadata 'bubbles' must be a non-empty list")

    if not isinstance(payload.get("question_items"), list) or len(payload["question_items"]) == 0:
        raise InvalidMetadataError("metadata 'question_items' must be a non-empty list")
