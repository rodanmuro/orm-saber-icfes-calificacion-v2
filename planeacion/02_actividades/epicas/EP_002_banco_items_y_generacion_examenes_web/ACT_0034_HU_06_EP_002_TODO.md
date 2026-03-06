estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0034 - Gestion de examenes y asociacion de items

## Objetivo tecnico
Implementar la gestion de examenes asociados a docente y la relacion N:M con items del banco para preparar versiones aplicables.

## Tareas implementables
- [ ] Definir entidades `exam` y `exam_item` en backend.
- [ ] Aplicar restriccion de negocio `UNIQUE(teacher_id, exam_code)`.
- [ ] Implementar endpoints para crear examen y asociar/desasociar items.
- [ ] Exponer en frontend web flujo de armado de examen desde banco de items.
- [ ] Validar persistencia de orden inicial de preguntas por examen.

## Evidencias esperadas
- Modelo de datos de examen e items asociados.
- Endpoints funcionales para gestion de examenes.
- Evidencia de armado de examen desde UI web.

## Criterio de terminado
El sistema permite crear examenes por docente y asociarles preguntas del banco con trazabilidad de orden.
