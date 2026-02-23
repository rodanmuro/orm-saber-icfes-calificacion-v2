estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0010 - Generacion de JSON de lectura por pregunta

## Objetivo tecnico
Construir salida JSON estructurada por `question_items` y opciones, con estados de marcacion y metadatos de calidad basicos.

## Tareas implementables
- [x] Definir esquema de salida para lectura OMR local.
- [x] Mapear resultados de burbujas a estructura por pregunta/opcion.
- [x] Agregar metadatos minimos (`template_id`, `version`, `timestamp`, resumen de calidad).
- [x] Validar consistencia entre cantidad esperada y cantidad reportada.

## Evidencias esperadas
- Constructor de salida OMR por pregunta:
  - `src/backend/app/modules/omr_reader/result_builder.py`
- CLI de clasificacion actualizado para exportar JSON final por pregunta:
  - `src/backend/app/modules/omr_reader/scripts/classify_bubbles.py`
- Documentacion corta del esquema de salida:
  - `src/backend/README.md`
- Pruebas automáticas de consistencia y estructura:
  - `src/backend/tests/test_omr_result_builder.py`

## Criterio de terminado
El JSON final representa todas las preguntas y opciones esperadas sin omisiones ni duplicados.
