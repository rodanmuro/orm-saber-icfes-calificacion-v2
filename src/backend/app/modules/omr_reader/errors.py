from __future__ import annotations


class OMRReadInputError(Exception):
    """Base error for local OMR read input stage."""


class InputFileNotFoundError(OMRReadInputError):
    """Raised when required image or metadata file is missing."""


class InvalidImageError(OMRReadInputError):
    """Raised when image cannot be decoded as a valid matrix."""


class InvalidMetadataError(OMRReadInputError):
    """Raised when metadata is invalid or incomplete for read stage."""


class ArucoDetectionError(OMRReadInputError):
    """Raised when required ArUco markers cannot be detected."""


class HomographyError(OMRReadInputError):
    """Raised when image alignment via homography fails."""


class CaptureQualityError(OMRReadInputError):
    """Raised when capture geometry quality is too poor for reliable OMR."""


class BubbleReadError(OMRReadInputError):
    """Raised when bubble classification cannot be completed."""


class UnsupportedReaderBackendError(OMRReadInputError):
    """Raised when a configured OMR reader backend is not supported."""


class ReaderBackendNotReadyError(OMRReadInputError):
    """Raised when a supported backend exists but is not implemented yet."""


class GeminiReadError(OMRReadInputError):
    """Raised when Gemini read fails due to network, auth, or invalid output."""


class OpenAIReadError(OMRReadInputError):
    """Raised when OpenAI read fails due to network, auth, or invalid output."""
