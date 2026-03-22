from __future__ import annotations

from app.modules.item_ai_assistant.domain import GenerateItemDraftInput

PROMPT_VERSION = "v2_correct_answer_a"


def build_system_prompt() -> str:
    return (
        "Eres un asistente para redactar items de seleccion multiple tipo ICFES. "
        "Responde solo JSON valido, sin markdown ni texto adicional. "
        "Debes devolver exactamente este objeto JSON: "
        "{\"statement\": string, \"options\": {\"A\": string, \"B\": string, \"C\": string, \"D\": string}, \"correct_answer\": \"A\"|\"B\"|\"C\"|\"D\"}. "
        "No agregues campos adicionales. "
        "Regla obligatoria: la respuesta correcta debe ubicarse en la opcion A."
    )


def build_user_prompt(data: GenerateItemDraftInput) -> str:
    subject = data.subject or "no especificada"
    difficulty = data.difficulty or "no especificada"
    return (
        "Contexto curricular obligatorio:\n"
        f"- standard_name: {data.standard_name}\n"
        f"- competency_name: {data.competency_name}\n"
        f"- subject: {subject}\n"
        f"- difficulty: {difficulty}\n\n"
        "Instruccion docente:\n"
        f"{data.user_prompt.strip()}\n\n"
        "Genera un item de opcion multiple con 4 opciones (A-D) y una sola correcta. "
        "Ubica siempre la respuesta correcta en la opcion A."
    )
