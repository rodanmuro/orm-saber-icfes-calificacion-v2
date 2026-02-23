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


class BubbleReadError(OMRReadInputError):
    """Raised when bubble classification cannot be completed."""
