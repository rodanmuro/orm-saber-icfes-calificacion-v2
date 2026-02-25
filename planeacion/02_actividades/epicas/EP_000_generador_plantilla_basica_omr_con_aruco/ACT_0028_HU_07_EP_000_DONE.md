estado: done
prioridad: alta
sprint: S3
owner: codex

# ACT_0028 - Extender esquema y generar metadata oficial v2

## Objetivo tecnico
Extender el contrato de template para soportar bloques auxiliares y generar artefactos `template_basica_omr_v2` coexistiendo con `v1`.

## Tareas implementables
- [x] Extender modelos de contratos para `auxiliary_blocks`.
- [x] Integrar validacion de bloques auxiliares en layout engine.
- [x] Crear configuracion `template.basica_omr_v2.json`.
- [x] Generar `template_basica_omr_v2.json` y `template_basica_omr_v2.pdf`.
- [x] Verificar que `template_basica_omr_v1.json` permanece intacto.

## Evidencias esperadas
- `src/backend/app/modules/template_generator/contracts.py`
- `src/backend/app/modules/template_generator/layout_engine.py`
- `src/backend/config/template.basica_omr_v2.json`
- `src/backend/data/output/template_basica_omr_v2.json`

## Cierre breve
La plantilla v2 ya existe como metadata formal en paralelo a v1, habilitando evolucion del lector sin romper flujo actual.

## Criterio de terminado
Se dispone de v2 generada y validada con convivencia explicita de v1/v2.
