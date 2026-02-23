estado: done
prioridad: media
sprint: S1
owner: codex

# ACT_0003 - Construir bloque rectangular principal parametrico

## Objetivo tecnico
Definir y renderizar el bloque principal de lectura como entidad geometrica configurable y desacoplada de ArUco/burbujas.

## Tareas implementables
- [x] Parametrizar posicion y dimensiones del bloque principal.
- [x] Implementar reglas de validacion geometrica (sin colision con ArUco).
- [x] Exponer `main_block_bbox` como salida para consumo de otros modulos.
- [x] Dibujar bloque en renderer sin dependencias directas a logica de burbujas.

## Evidencias esperadas
- Plantilla con bloque principal visible en `src/backend/output/template_basica_omr_v1.pdf`.
- Metadato del bloque principal exportable en `src/backend/output/template_basica_omr_v1.json` (`main_block_bbox` y `block`).
- Validaciones de consistencia en:
  - `src/backend/app/modules/template_generator/layout_engine.py`
  - `src/backend/tests/test_layout_engine.py`
  - `src/backend/tests/test_pipeline.py`

## Criterio de terminado
El bloque puede moverse/escalarse desde configuracion manteniendo consistencia y sin romper ArUco.
