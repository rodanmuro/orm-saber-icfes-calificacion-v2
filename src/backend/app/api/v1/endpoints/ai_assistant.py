from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.item_ai_assistant.domain import GenerateItemDraftInput
from app.modules.item_ai_assistant.errors import (
    ItemAIAssistantProviderError,
    ItemAIAssistantValidationError,
)
from app.modules.item_ai_assistant.media_service import GenerateMediaInput, generate_media_from_spec
from app.modules.item_ai_assistant.service import generate_item_draft
from app.schemas.item_ai_assistant import (
    GenerateItemAIPayload,
    GenerateItemAIResponse,
    GenerateMediaPayload,
    GenerateMediaResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate-item", response_model=GenerateItemAIResponse)
def generate_item_with_ai(payload: GenerateItemAIPayload) -> GenerateItemAIResponse:
    try:
        result = generate_item_draft(
            GenerateItemDraftInput(
                user_prompt=payload.user_prompt,
                standard_name=payload.standard_name,
                competency_name=payload.competency_name,
                subject=payload.subject,
                difficulty=payload.difficulty,
            )
        )
    except ItemAIAssistantValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ItemAIAssistantProviderError as exc:
        if "OPENAI_API_KEY" in str(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI provider failed to generate item: {str(exc)}",
        ) from exc

    return GenerateItemAIResponse(
        statement_doc=result.statement_doc,
        options_doc=result.options_doc,
        correct_answer=result.correct_answer,
        metadata=result.metadata,
        usage=result.usage,
        media_spec=result.media_spec,
        media_specs=result.media_specs or [],
    )


@router.post("/generate-media", response_model=GenerateMediaResponse)
def generate_media(payload: GenerateMediaPayload) -> GenerateMediaResponse:
    try:
        result = generate_media_from_spec(
            GenerateMediaInput(
                teacher_id=payload.teacher_id,
                mode=payload.mode,
                target=payload.target,
                spec=payload.spec,
            )
        )
    except ItemAIAssistantValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return GenerateMediaResponse(
        asset=result.asset,
        insert_doc=result.insert_doc,
        meta=result.meta,
    )
