estado: todo
prioridad: alta
sprint: S5
owner: por_definir

# ACT_0042 - UI movil para seleccionar examen y version

## Objetivo tecnico
Permitir que la app movil liste examenes y versiones publicadas, y seleccione una combinacion antes de enviar la lectura OMR.

## Tareas implementables
- [ ] Consumir endpoint de examenes por docente (default teacher) desde movil.
- [ ] Consultar versiones publicadas por examen y mostrarlas en UI.
- [ ] Guardar seleccion de examen/version como contexto de calificacion.
- [ ] Bloquear flujo si no hay versiones publicadas con mensaje claro.

## Evidencias esperadas
- Pantallas en movil con seleccion examen/version.
- Payload enviado al backend con `exam_id` y `version_id`.

## Criterio de terminado
La app movil no permite calificar sin seleccionar examen y version publicada.
