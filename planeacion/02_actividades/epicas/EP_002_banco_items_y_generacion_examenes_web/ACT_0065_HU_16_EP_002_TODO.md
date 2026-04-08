estado: todo
prioridad: media
sprint: S9
owner: por_definir

# ACT_0065 - Integracion frontend para descarga de examen en PDF

## Objetivo tecnico
Integrar en `Armado de examen` la accion de exportar/descargar PDF del cuadernillo de preguntas de una version publicada, con feedback claro de estado y error.

## Tareas implementables
- [ ] Agregar accion de `Descargar PDF` por fila de version publicada en frontend.
- [ ] Consumir endpoint backend de exportacion con manejo de `blob` y nombre de archivo trazable.
- [ ] Mostrar estados de UX: generando, descargando, error de exportacion.
- [ ] Incluir metadatos visibles de version para evitar descarga de version equivocada.
- [ ] Agregar prueba E2E/manual guiada del flujo: seleccionar examen -> seleccionar version -> descargar PDF.
- [ ] Documentar comando/flujo de validacion para equipo (README o bitacora tecnica).

## Evidencias esperadas
- Descarga funcional de PDF desde la pestaña `Armado de examen`.
- Nombre de archivo consistente con `exam_code` y `version_code`.
- Mensajes de error accionables cuando la exportacion falla.

## Criterio de terminado
El docente puede descargar desde frontend un PDF imprimible de una version publicada sin pasos manuales externos.
El alcance de esta actividad corresponde al cuadernillo de preguntas (no a la hoja OMR de respuestas).
