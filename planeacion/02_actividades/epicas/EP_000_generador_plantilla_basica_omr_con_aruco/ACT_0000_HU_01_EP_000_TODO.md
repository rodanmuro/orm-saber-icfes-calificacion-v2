estado: todo
prioridad: alta
sprint: S1
owner: por_definir

# ACT_0000 - Base arquitectonica modular y parametrizable

## Objetivo tecnico
Definir la arquitectura del generador de plantilla separando responsabilidades y contratos de configuracion para evitar hardcode y facilitar escalabilidad.

## Tareas implementables
- [ ] Definir modulos base en `src/`:
- [ ] `config_loader` (lectura/validacion de configuracion).
- [ ] `layout_engine` (calculo geometrico).
- [ ] `aruco_renderer` (generacion/posicionamiento ArUco).
- [ ] `bubble_layout` (calculo de burbujas OMR).
- [ ] `template_renderer` (salida visual).
- [ ] `metadata_exporter` (salida estructurada).
- [ ] Definir contratos/DTOs para `page_config`, `aruco_config`, `block_config`, `bubble_config`.
- [ ] Documentar dependencias entre modulos evitando acoplamiento circular.

## Evidencias esperadas
- Estructura modular creada en `src/`.
- Documento corto de contratos de configuracion en `planeacion/` o `README` tecnico.

## Criterio de terminado
La arquitectura permite cambiar layout via configuracion sin modificar logica central del pipeline.
