from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel


class OMRReadInputContext(BaseModel):
    image_path: Path
    metadata_path: Path
    metadata: dict[str, Any]

    class Config:
        arbitrary_types_allowed = True


class OMRReadImageContext(OMRReadInputContext):
    image: np.ndarray

    class Config:
        arbitrary_types_allowed = True


class OMRAlignmentResult(BaseModel):
    aligned_image: np.ndarray
    homography: np.ndarray
    detected_marker_ids: list[int]
    output_width_px: int
    output_height_px: int

    class Config:
        arbitrary_types_allowed = True
