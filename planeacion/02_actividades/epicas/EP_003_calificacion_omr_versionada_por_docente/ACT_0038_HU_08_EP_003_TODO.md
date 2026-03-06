estado: todo
prioridad: media
sprint: S4
owner: por_definir

# ACT_0038 - Persistencia de intentos OMR y respuestas detalladas

## Objetivo tecnico
Persistir cada intento OMR con su resultado de calificacion y detalle por pregunta para habilitar auditoria y consultas posteriores.

## Tareas implementables
- [ ] Definir entidades `omr_attempt` y `omr_attempt_answer`.
- [ ] Persistir estado final del intento (graded, needs_review, error).
- [ ] Persistir detalle de respuesta marcada, correcta/incorrecta y ambiguedades.
- [ ] Asociar intento a `exam_version` y `student` cuando aplique.
- [ ] Validar consultas basicas por intento y por examen/version.

## Evidencias esperadas
- Tablas y repositorios de persistencia de intentos.
- Flujo backend que guarda resultado estructurado al finalizar calificacion.
- Pruebas de integridad de datos por intento.

## Criterio de terminado
El sistema registra y recupera de forma consistente intentos OMR con trazabilidad de resultado por pregunta.
