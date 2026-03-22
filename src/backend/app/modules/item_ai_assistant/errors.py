class ItemAIAssistantError(Exception):
    """Base error for AI item assistant module."""


class ItemAIAssistantValidationError(ItemAIAssistantError):
    """Raised when model output does not satisfy strict item contract."""


class ItemAIAssistantProviderError(ItemAIAssistantError):
    """Raised when provider call fails or returns unusable content."""
