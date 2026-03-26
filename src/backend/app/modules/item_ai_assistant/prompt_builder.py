from __future__ import annotations

from app.modules.item_ai_assistant.domain import GenerateItemDraftInput

PROMPT_VERSION = "v5_1_table_required_and_concise_option_media"


def build_system_prompt() -> str:
    return (
        "Eres un asistente para redactar items de seleccion multiple tipo ICFES. "
        "Responde solo JSON valido, sin markdown ni texto adicional. "
        "Debes devolver exactamente este objeto JSON: "
        "{"
        "\"statement_doc\": TipTapDoc, "
        "\"options_doc\": {\"A\": TipTapDoc, \"B\": TipTapDoc, \"C\": TipTapDoc, \"D\": TipTapDoc}, "
        "\"correct_answer\": \"A\"|\"B\"|\"C\"|\"D\", "
        "\"media_specs\": []|[{\"mode\":\"chart_deterministic\",\"target\":\"statement\"|\"option_a\"|\"option_b\"|\"option_c\"|\"option_d\",\"spec\":{...}}]"
        "}. "
        "No agregues campos adicionales. "
        "TipTapDoc debe usar estructura {type:\"doc\", content:[...]} con parrafos y nodos inline. "
        "Si necesitas ecuaciones, usa nodos {type:\"mathInline\", attrs:{latex:\"...\"}} dentro de un parrafo. "
        "No uses delimitadores $...$ ni $$...$$ dentro de latex. "
        "Para simbolo de moneda dolar usa \\$ en latex. "
        "Regla obligatoria: la respuesta correcta debe ubicarse en la opcion A. "
        "Si la instruccion requiere grafico o figura cuantitativa, entrega media_specs con uno o mas graficos (maximo 5) "
        "y chart_type permitido ('bar' o 'pie') con datos completos y targets unicos. "
        "Si no se necesita grafico, media_specs debe ser lista vacia. "
        "Si entregas media_specs para graficos, no repitas en statement_doc los valores numericos exactos por categoria; "
        "el enunciado debe referirse a la grafica para que el estudiante lea los datos desde ella."
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
        "Ubica siempre la respuesta correcta en la opcion A. "
        "Preferir contenido matematico con nodos mathInline cuando aplique. "
        "Si el docente solicita graficos, usa media_specs con uno o varios targets. "
        "En cada spec con chart_type=bar, labels es obligatorio y debe describir cada barra; "
        "values debe ser lista numerica pura (sin % ni texto) y tener misma longitud que labels. "
        "En chart_type=pie, usa sizes numerico (o values numerico) con la misma longitud que labels. "
        "Si generas grafico, redacta el enunciado sin listar explicitamente los valores por categoria. Si la instruccion pide tabla, construye un nodo table en statement_doc. Si una opcion tiene grafica, usa texto corto en esa opcion y evita describir la grafica en palabras."
    )
