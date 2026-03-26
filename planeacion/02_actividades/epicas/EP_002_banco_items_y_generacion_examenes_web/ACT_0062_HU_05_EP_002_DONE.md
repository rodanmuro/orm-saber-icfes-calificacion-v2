estado: done
prioridad: media
sprint: S8
owner: por_definir

# ACT_0062 - Compactacion de toolbar y hardening de tablas en editor enriquecido

## Objetivo tecnico
Mejorar usabilidad del editor enriquecido reduciendo ocupacion visual de la toolbar y estabilizando el comportamiento de seleccion/edicion de tablas.

## Tareas implementables
- [ ] Compactar controles de toolbar (tamano, agrupacion, iconografia y tooltips).
- [ ] Mover acciones de tabla a un menu desplegable para reducir saturacion de botones.
- [ ] Corregir comportamiento visual de seleccion de celdas para evitar overlays fuera de la tabla.
- [ ] Mantener edicion directa de celdas sin bloquear flujo normal de texto.
- [ ] Conservar resize por columnas sin degradar layout global del editor.
- [ ] Validar build frontend y pruebas manuales en casos de tabla simple y tabla compleja.

## Evidencias esperadas
- Toolbar mas compacta y legible en flujo diario.
- Seleccion de tablas estable y acotada al componente tabla.
- Evidencia de no-regresion en insercion de imagen, ecuaciones y texto.

## Criterio de terminado
El editor permite trabajar con tablas y herramientas frecuentes sin saturacion visual ni fallos de seleccion.

