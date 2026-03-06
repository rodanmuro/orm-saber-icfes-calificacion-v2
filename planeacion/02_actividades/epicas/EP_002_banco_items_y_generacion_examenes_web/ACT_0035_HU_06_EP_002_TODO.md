estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0035 - Publicacion de version de examen con barajado

## Objetivo tecnico
Implementar la publicacion de versiones inmutables de examen con barajado de orden de preguntas y/o opciones por pregunta, manteniendo mapeo correcto de respuestas.

## Tareas implementables
- [ ] Definir entidades `exam_version` y `exam_version_item`.
- [ ] Implementar proceso de publicacion de version con `seed_shuffle` reproducible.
- [ ] Generar y persistir `option_map` por pregunta para versiones barajadas.
- [ ] Validar almacenamiento de `correct_answer_mapped` por version.
- [ ] Exponer endpoint para publicar y consultar versiones.

## Evidencias esperadas
- Versiones de examen persistidas con estado inmutable.
- Evidencia de al menos dos versiones diferentes del mismo examen.
- Pruebas de consistencia del mapeo de respuesta correcta tras barajado.

## Criterio de terminado
El sistema puede publicar versiones de examen con variaciones controladas y trazables, listas para aplicacion/calificacion.
