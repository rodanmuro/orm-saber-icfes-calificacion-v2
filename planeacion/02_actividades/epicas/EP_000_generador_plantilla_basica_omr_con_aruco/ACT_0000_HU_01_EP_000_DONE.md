estado: done
prioridad: alta
sprint: S1
owner: codex

# ACT_0000 - Base arquitectonica modular y parametrizable

## Objetivo tecnico
Definir la arquitectura del generador de plantilla separando responsabilidades y contratos de configuracion para evitar hardcode y facilitar escalabilidad.

## Tareas implementables
- [x] Definir modulos base en `src/`:
- [x] `config_loader` (lectura/validacion de configuracion).
- [x] `layout_engine` (calculo geometrico).
- [x] `aruco_renderer` (generacion/posicionamiento ArUco).
- [x] `bubble_layout` (calculo de burbujas OMR).
- [x] `template_renderer` (salida visual).
- [x] `metadata_exporter` (salida estructurada).
- [x] Definir contratos/DTOs para `page_config`, `aruco_config`, `block_config`, `bubble_config`.
- [x] Documentar dependencias entre modulos evitando acoplamiento circular.

## Evidencias esperadas
- Estructura modular creada en `src/backend/app/modules/template_generator/`.
- Documento de contratos y dependencias en `src/backend/README.md`.

## Criterio de terminado
La arquitectura permite cambiar layout via configuracion sin modificar logica central del pipeline.
