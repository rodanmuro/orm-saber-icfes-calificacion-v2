# Bitacora 020_02_24_2026 11:18:54 avance_act_0023_pruebas_llm

## Que fue lo que se hizo
- Se completo la integracion funcional del motor alterno Gemini en el backend bajo estrategia de lectores.
- Se agrego trazabilidad operativa en logs y respuestas para motores LLM:
  - backend activo (`reader_backend`),
  - uso de tokens,
  - latencia de inferencia del modelo,
  - tiempo total de solicitud.
- Se agrego reporte estructurado para dudas de lectura (`ambiguous_questions`, `unreadable_questions`) y se reforzo la regla para que preguntas sin opcion marcada queden registradas como no legibles.
- Se habilito y probo un segundo motor alterno (`openai`) bajo la misma interfaz del backend.
- Se implemento preprocesado para LLM antes de inferencia:
  - alineacion por ArUco + homografia,
  - recorte del bloque de respuestas,
  - mejora de contraste (CLAHE),
  - envio al modelo de imagen preprocesada (no foto cruda).
- Se ejecutaron pruebas E2E reales desde movil con ambos motores y comparacion contra clave esperada.

### Archivos creados/modificados relevantes
- `src/backend/app/modules/omr_reader/reader_strategy.py`
- `src/backend/app/modules/omr_reader/api_service.py`
- `src/backend/app/modules/omr_reader/errors.py`
- `src/backend/app/modules/omr_reader/gemini_reader.py`
- `src/backend/app/modules/omr_reader/openai_reader.py`
- `src/backend/app/modules/omr_reader/llm_preprocess.py`
- `src/backend/app/modules/omr_reader/scripts/ping_gemini.py`
- `src/backend/app/api/v1/endpoints/omr_read.py`
- `src/backend/app/core/config.py`
- `src/backend/tests/test_omr_api_service.py`
- `src/backend/tests/test_gemini_reader.py`
- `src/backend/tests/test_openai_reader.py`
- `src/backend/requirements.txt`

## Para que se hizo
- Validar el enfoque de doble motor (clasico + LLM) sin perder compatibilidad del contrato JSON existente.
- Medir en entorno real el tradeoff precision vs latencia de motores LLM.
- Preparar base para flujo operativo con estados (`pending`, `done`, `error`, `revisar`) y procesamiento asíncrono en siguientes actividades.

## Que problemas se presentaron
- Dependencias faltantes en entorno para llamadas reales (`google-genai`, `openai`).
- Variabilidad de latencia de inferencia remota en pruebas reales.
- Resultados inconsistentes en OpenAI aun con preprocesado (errores de mapeo pregunta-opcion).
- Warning de SDK Gemini por partes no textuales (`thought_signature`).

## Como se resolvieron
- Se instalaron dependencias necesarias y se validaron pings reales a APIs.
- Se agregaron logs de latencia y tokens para trazabilidad objetiva por solicitud.
- Se reforzo parser/reporte para marcar preguntas sin respuesta como `unreadable`.
- Se aplico preprocesado previo a LLM para mejorar calidad de entrada (alineacion + crop + CLAHE).
- Se consolidaron pruebas E2E sobre fotos reales:
  - Gemini 3.x con exactitud consistente alta (30/30 en varias corridas) pero latencia alta.
  - OpenAI con menor latencia relativa, pero precision insuficiente en las corridas actuales.

## Que continua
- Cerrar formalmente `ACT_0023` con evidencia consolidada (logs, tokens, latencia, exactitud por motor).
- Iniciar `ACT_0024` para formalizar operacion por motor y politica de fallback.
- Diseñar/implementar flujo asíncrono por trabajos (`pending/processing/done/error/revisar`) para compensar latencia de LLM en uso movil.
- Avanzar a benchmark comparativo sistematico (`ACT_0025`) para decision de motor por defecto en produccion.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
