estado: done
prioridad: alta
sprint: S1
owner: codex

# ACT_0001 - Implementar layout base carta parametrico

## Objetivo tecnico
Implementar el calculo de pagina carta y margenes mediante configuracion externa, sin coordenadas hardcodeadas en el flujo principal.

## Tareas implementables
- [x] Definir archivo de configuracion base (JSON/YAML) con dimensiones y margenes.
- [x] Implementar parser y validaciones de rangos (ancho, alto, margenes).
- [x] Construir funciones puras de geometria para marco util de trabajo.
- [x] Conectar `layout_engine` con `template_renderer` sin literals geometrico fijos.

## Evidencias esperadas
- Config base versionada en `src/backend/config/template.base.json`.
- Parser JSON/YAML implementado en `src/backend/app/modules/template_generator/config_loader.py`.
- Funciones puras de geometria en `src/backend/app/modules/template_generator/geometry.py`.
- Regeneracion de plantilla y metadatos con config JSON y YAML en `src/backend/output/`.

## Criterio de terminado
Cambiar margenes o dimensiones en config altera la salida sin editar codigo fuente del motor geometrico.
