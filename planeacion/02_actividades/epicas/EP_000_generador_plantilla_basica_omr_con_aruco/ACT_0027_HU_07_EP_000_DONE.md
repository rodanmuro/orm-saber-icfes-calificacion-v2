estado: done
prioridad: alta
sprint: S3
owner: codex

# ACT_0027 - Wireframe v2 de plantilla con nuevos recuadros

## Objetivo tecnico
Construir un wireframe PDF iterativo para definir la geometria final de la plantilla v2 sin afectar la plantilla oficial v1.

## Tareas implementables
- [x] Crear script dedicado de wireframe para ArUco + recuadros.
- [x] Ajustar layout superior (header, documento, identidad, identificacion examen).
- [x] Ajustar recuadro de respuestas y mock de distribucion de preguntas.
- [x] Aplicar estilo visual de baja interferencia OMR en texto interno de burbujas.

## Evidencias esperadas
- `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`
- `src/backend/data/output/template_wireframe_layout_v1.pdf`

## Cierre breve
Se definio una geometria v2 aceptable a nivel visual y operativa para continuar con metadata formal y lector.

## Criterio de terminado
Existe wireframe reproducible que representa la propuesta de plantilla v2.
