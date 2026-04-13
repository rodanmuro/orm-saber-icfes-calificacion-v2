estado: done
prioridad: media
sprint: S9
owner: por_definir

# ACT_0065 - Integracion frontend para descarga de examen (PDF y DOCX)

## Objetivo tecnico
Integrar en `Armado de examen` las acciones de exportar/descargar PDF y DOCX de una version publicada, con feedback claro de estado y error.

## Tareas implementables
- [x] Agregar accion de `Exportar a PDF` en tabla `Examenes del docente` (usa ultima version publicada).
- [x] Consumir endpoint backend de exportacion PDF con manejo de `blob` y nombre de archivo trazable.
- [x] Agregar accion de `Exportar a DOCX` en tabla `Examenes del docente` para la ultima version publicada.
- [x] Mostrar mensajes de UX para exito/error de exportacion.
- [x] Incluir validacion de precondicion: examen sin versiones publicadas no exporta.
- [x] Documentar convencion de nombre de archivo (`exam_code` + `version_code`).

## Evidencias esperadas
- Descarga funcional de PDF desde la pestaña `Armado de examen`.
- Descarga funcional de DOCX desde la pestaña `Armado de examen`.
- Nombre de archivo consistente con `exam_code` y `version_code`.
- Mensajes de error accionables cuando la exportacion falla.

## Criterio de terminado
El docente puede descargar desde frontend un PDF imprimible y un DOCX de una version publicada sin pasos manuales externos.
El alcance de esta actividad corresponde al cuadernillo de preguntas (no a la hoja OMR de respuestas).
