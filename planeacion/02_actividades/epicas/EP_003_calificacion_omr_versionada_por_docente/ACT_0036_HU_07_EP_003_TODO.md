estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0036 - Resolucion de examen por docente y codigo OMR

## Objetivo tecnico
Resolver el examen aplicado desde lectura OMR en contexto de docente usando la clave de negocio `teacher_id + exam_code`.

## Tareas implementables
- [ ] Integrar resolucion de `exam_code` detectado contra examenes del docente.
- [ ] Definir manejo de errores controlados para casos sin coincidencia o ambiguos.
- [ ] Incorporar trazabilidad de resolucion (docente, examen, version) en diagnosticos.
- [ ] Cubrir casos de prueba de resolucion valida e invalida.

## Evidencias esperadas
- Flujo de resolucion documentado y probado.
- Logs/diagnosticos con identificadores de contexto academico.
- Pruebas automatizadas de escenarios limite.

## Criterio de terminado
Cada lectura OMR se enlaza de forma deterministica a un examen/version en contexto de docente o retorna error controlado.
