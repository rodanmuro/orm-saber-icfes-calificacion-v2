estado: done
prioridad: alta
sprint: S1
owner: codex

# ACT_0005 - Exportar metadatos de plantilla como fuente de verdad

## Objetivo tecnico
Implementar exportacion de metadatos (`template.json` o equivalente) desacoplada del renderer visual, con esquema consistente y validable.

## Tareas implementables
- [x] Definir esquema minimo: pagina, ArUco, bloque principal, burbujas, version de plantilla.
- [x] Implementar `metadata_exporter` independiente del backend de render.
- [x] Asegurar correspondencia 1:1 entre elementos renderizados y metadatos.
- [x] Agregar validacion de esquema (campos requeridos/tipos).
- [x] Incluir en renderer PDF la incrustacion de marcadores ArUco reales para pruebas de escaneo movil.

## Evidencias esperadas
- Archivo de metadatos generado por ejecucion en `src/backend/output/template_basica_omr_v1.json`.
- Validacion automatica basica en tests (`src/backend/tests/test_pipeline.py`).
- Soporte de marcadores ArUco reales en:
  - `src/backend/app/modules/template_generator/aruco_assets.py`
  - `src/backend/app/modules/template_generator/template_renderer.py`

## Criterio de terminado
El archivo de metadatos describe por completo la geometria necesaria para lectura OMR sin inferencias manuales.
