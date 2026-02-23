estado: todo
prioridad: media
sprint: S1
owner: por_definir

# ACT_0003 - Construir bloque rectangular principal parametrico

## Objetivo tecnico
Definir y renderizar el bloque principal de lectura como entidad geometrica configurable y desacoplada de ArUco/burbujas.

## Tareas implementables
- [ ] Parametrizar posicion y dimensiones del bloque principal.
- [ ] Implementar reglas de validacion geometrica (sin colision con ArUco).
- [ ] Exponer `main_block_bbox` como salida para consumo de otros modulos.
- [ ] Dibujar bloque en renderer sin dependencias directas a logica de burbujas.

## Evidencias esperadas
- Plantilla con bloque principal visible.
- Metadato del bloque principal exportable.

## Criterio de terminado
El bloque puede moverse/escalarse desde configuracion manteniendo consistencia y sin romper ArUco.
