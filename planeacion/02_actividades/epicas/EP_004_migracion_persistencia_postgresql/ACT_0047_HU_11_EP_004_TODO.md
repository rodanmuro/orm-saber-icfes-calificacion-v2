estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0047 - Validacion de calificacion y persistencia OMR sobre PostgreSQL

## Objetivo tecnico
Confirmar operacion de EP_003 en PostgreSQL (scoring, persistencia de intentos y trazabilidad de evidencias).

## Tareas implementables
- [ ] Ejecutar lectura/calificacion OMR con examen identificado por docente + exam_code.
- [ ] Validar persistencia de `omr_attempt` y `omr_attempt_answer`.
- [ ] Verificar consulta estructurada de intentos y resultados.
- [ ] Ajustar incompatibilidades de consultas/constraints detectadas en PostgreSQL.

## Evidencias esperadas
- Flujo OMR versionado operando sobre PostgreSQL.
- Evidencia de intentos persistidos con detalle por pregunta.
- Pruebas criticas EP_003 en verde.

## Criterio de terminado
La calificacion OMR versionada por docente funciona y persiste trazabilidad completa en PostgreSQL.
