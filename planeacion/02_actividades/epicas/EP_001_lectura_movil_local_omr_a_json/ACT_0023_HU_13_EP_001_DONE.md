estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0023 - Integracion de lector Gemini con salida estructurada

## Objetivo tecnico
Integrar lector LLM Gemini en backend bajo el contrato comun de lectura OMR, con salida estructurada y trazabilidad operativa.

## Tareas implementables
- [x] Crear adaptador Gemini en backend con cliente/configuracion de modelo.
- [x] Definir prompt tecnico de lectura OMR con formato de salida estricto.
- [x] Validar/parsear respuesta con esquema tipado.
- [x] Manejar errores de red/cuota/timeout con respuesta controlada.
- [x] Registrar uso de tokens, reporte de ambiguedad y latencia de modelo.

## Evidencias esperadas
- Integracion backend:
  - `src/backend/app/modules/omr_reader/gemini_reader.py`
  - `src/backend/app/modules/omr_reader/reader_strategy.py`
  - `src/backend/app/modules/omr_reader/api_service.py`
- Configuracion/diagnostico:
  - `src/backend/app/core/config.py`
  - `src/backend/app/modules/omr_reader/scripts/ping_gemini.py`
- Pruebas:
  - `src/backend/tests/test_gemini_reader.py`

## Cierre breve
Gemini quedo integrado y operativo e2e bajo el mismo contrato del motor classic. La comparacion de precision/costo/latencia queda para ACT_0024, ACT_0025 y ACT_0026.

## Criterio de terminado
El backend procesa al menos una imagen usando `gemini` y devuelve JSON valido bajo el contrato comun.
