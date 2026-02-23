estado: done
prioridad: alta
sprint: S1
owner: codex

# ACT_0002 - Integrar ArUco en esquinas de forma configurable

## Objetivo tecnico
Generar y ubicar 4 ArUco en esquinas logicas usando parametros configurables de diccionario, tamano y offset.

## Tareas implementables
- [x] Parametrizar `aruco_dictionary`, IDs permitidos y `marker_size`.
- [x] Parametrizar offsets por esquina respecto a margenes.
- [x] Implementar validacion para evitar ArUco fuera del area imprimible.
- [x] Exponer coordenadas finales de ArUco para metadatos.

## Evidencias esperadas
- Implementacion de offsets por esquina y validaciones de diccionario/IDs en `src/backend/app/modules/template_generator/contracts.py`.
- Posicionamiento ArUco basado en area imprimible en `src/backend/app/modules/template_generator/aruco_renderer.py`.
- Validacion de marcadores fuera de area imprimible y colision con bloque en `src/backend/app/modules/template_generator/layout_engine.py`.
- Configuracion versionada con offsets por esquina en `src/backend/config/template.base.json`.
- Tests automaticos de contratos/layout/renderer en `src/backend/tests/`.

## Criterio de terminado
El sistema permite cambiar diccionario/tamano/offset de ArUco por config y mantiene 4 marcadores validos en la salida.
