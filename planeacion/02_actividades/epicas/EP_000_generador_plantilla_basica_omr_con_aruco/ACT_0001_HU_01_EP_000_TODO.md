estado: todo
prioridad: alta
sprint: S1
owner: por_definir

# ACT_0001 - Implementar layout base carta parametrico

## Objetivo tecnico
Implementar el calculo de pagina carta y margenes mediante configuracion externa, sin coordenadas hardcodeadas en el flujo principal.

## Tareas implementables
- [ ] Definir archivo de configuracion base (JSON/YAML) con dimensiones y margenes.
- [ ] Implementar parser y validaciones de rangos (ancho, alto, margenes).
- [ ] Construir funciones puras de geometria para marco util de trabajo.
- [ ] Conectar `layout_engine` con `template_renderer` sin literals geometrico fijos.

## Evidencias esperadas
- Archivo de config versionado en repositorio.
- Salida visual de plantilla con pagina carta y margenes respetados.

## Criterio de terminado
Cambiar margenes o dimensiones en config altera la salida sin editar codigo fuente del motor geometrico.
