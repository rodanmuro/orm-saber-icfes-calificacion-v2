estado: todo
prioridad: alta
sprint: S3
owner: por_definir

# ACT_0030 - Implementar lectura de plantilla v2 y bloques auxiliares

## Objetivo tecnico
Extender el lector OMR backend para procesar `template_basica_omr_v2.json`, leyendo bloques auxiliares (`DOCUMENTO`, `NUMERO DE IDENTIDAD`, `IDENTIFICACION EXAMEN`) ademas del bloque de respuestas, manteniendo compatibilidad completa con v1.

## Tareas implementables
- [ ] Incorporar parseo de `auxiliary_blocks` en el flujo de lectura backend.
- [ ] Implementar lectura OMR para bloque `document_type` con seleccion unica.
- [ ] Implementar lectura OMR para bloque `student_identity_number` (10x12, una marca por columna).
- [ ] Implementar lectura OMR para bloque `exam_identifier` (10x4, una marca por columna).
- [ ] Definir salida estructurada v2 para identidad/examen con flags de `missing`/`ambiguous` por columna.
- [ ] Mantener salida actual de respuestas sin cambios contractuales para v1.
- [ ] Agregar pruebas unitarias e integracion para v2 + regresion v1.

## Evidencias esperadas
- Lector backend actualizado en:
  - `src/backend/app/modules/omr_reader/`
- Pruebas:
  - `src/backend/tests/` (nuevos casos v2 y regresion v1)
- Ejecucion local:
  - lectura valida de `data/output/template_basica_omr_v2.json`
  - compatibilidad intacta con `data/output/template_basica_omr_v1.json`

## Criterio de terminado
El backend retorna, en una sola respuesta, lectura de respuestas + identidad/examen para plantilla v2, y mantiene comportamiento estable para plantilla v1.
