from __future__ import annotations

from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError

VALID_OPTION_KEYS = ("A", "B", "C", "D")


def validate_context(*, standard_name: str, competency_name: str) -> None:
    if not standard_name.strip() or not competency_name.strip():
        raise ItemAIAssistantValidationError(
            "standard_name and competency_name are required"
        )


def validate_model_output(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ItemAIAssistantValidationError("model output must be a JSON object")

    statement = payload.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise ItemAIAssistantValidationError("statement must be a non-empty string")

    options = payload.get("options")
    if not isinstance(options, dict):
        raise ItemAIAssistantValidationError("options must be an object with A/B/C/D")

    keys = set(options.keys())
    if keys != set(VALID_OPTION_KEYS):
        raise ItemAIAssistantValidationError("options must contain exactly A, B, C and D")

    normalized_options: dict[str, str] = {}
    for key in VALID_OPTION_KEYS:
        value = options.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ItemAIAssistantValidationError(f"option {key} must be a non-empty string")
        normalized_options[key] = value.strip()

    correct_answer = payload.get("correct_answer")
    if not isinstance(correct_answer, str):
        raise ItemAIAssistantValidationError("correct_answer must be a string")

    normalized_correct = correct_answer.strip().upper()
    if normalized_correct not in VALID_OPTION_KEYS:
        raise ItemAIAssistantValidationError("correct_answer must be one of A, B, C or D")

    return {
        "statement": statement.strip(),
        "options": normalized_options,
        "correct_answer": normalized_correct,
    }
