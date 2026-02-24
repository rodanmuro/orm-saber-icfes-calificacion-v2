from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

BACKEND_CLASSIC = "classic"
BACKEND_GEMINI = "gemini"
SUPPORTED_OMR_BACKENDS = {BACKEND_CLASSIC, BACKEND_GEMINI}


@dataclass(frozen=True)
class OMRReadRequest:
    image_bytes: bytes
    metadata_path: str
    px_per_mm: float
    marked_threshold: float
    unmarked_threshold: float
    robust_mode: bool
    save_debug_artifacts: bool
    debug_base_name: str | None
    debug_output_dir: str


class OMRReadEngine(Protocol):
    def read(self, request: OMRReadRequest) -> dict[str, Any]:
        """Execute OMR read and return structured payload."""


def normalize_reader_backend(value: str | None) -> str:
    if value is None:
        return BACKEND_CLASSIC
    return value.strip().lower()
