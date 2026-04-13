estado: todo
prioridad: alta
sprint: S5
owner: por_definir

# ACT_0043 - Integracion backend de calificacion por examen/version seleccionada

## Objetivo tecnico
Aceptar en backend el contexto `exam_id` y `version_id` proveniente del movil y usarlo en el scoring.

## Tareas implementables
- [ ] Ajustar payload de calificacion para incluir `exam_id` y `version_id`.
- [ ] Validar que la version pertenezca al examen y este publicada.
- [ ] Integrar el `option_map` y clave correcta segun version seleccionada.
- [ ] Exponer errores controlados si la version no es valida o no coincide con docente.

## Evidencias esperadas
- Endpoint de calificacion recibe `exam_id`/`version_id`.
- Pruebas manuales con version correcta y error con version invalida.

## Criterio de terminado
El backend califica usando exclusivamente la version seleccionada por el movil.
