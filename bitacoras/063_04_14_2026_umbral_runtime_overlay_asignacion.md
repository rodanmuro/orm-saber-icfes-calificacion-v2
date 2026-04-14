# Bitacora 063_04_14_2026 11:49:29 umbral_runtime_overlay_asignacion

## Que fue lo que se hizo
- Se completo la configuracion runtime de umbrales OMR desde el backend, agregando endpoints para consultar y actualizar `marked` y `unmarked` sin migraciones ni reinicio de esquema.
- Se conecto el frontend web en la pestaña `Examenes calificados` para mostrar dos inputs decimales con los umbrales actuales y permitir su ajuste directo desde la interfaz.
- Se implemento un modal de `Ratios` con lectura de `ratios.csv` y `auxiliary.ratios.csv`, incluyendo resaltado visual del top ratio en bloques auxiliares.
- Se implemento un modal `Overlay` sobre imagen alineada, dibujando rectangulos verdes y rojos para facilitar la inspeccion visual de la lectura.
- Se agrego fallback para detectar `aligned_image_path` a partir del archivo `.aligned.jpg` aunque el trace json no incluya diagnostics completos.
- Se extendio el modal `Ver` para permitir reasignar examen, version y estudiante en intentos con `resolution_error` o identificacion incompleta.
- Se reemplazo el selector largo de estudiante por un input con autocompletado basado en documento y nombre.
- Se ajustaron estilos visuales de filas `needs_review`, filas sin marca y grosor de overlay para mejorar inspeccion manual.
- Archivos modificados: `src/backend/app/api/v1/endpoints/omr_read.py`, `src/backend/app/core/config.py`, `src/backend/app/modules/omr_reader/api_service.py`, `src/frontend/App.js`, `src/frontend_web/src/App.jsx`, `src/frontend_web/src/api/omrApi.js`, `src/frontend_web/src/components/AttemptList.jsx`, `src/frontend_web/src/styles.css`.

## Para que se hizo
- Para reducir el margen de error operativo al calificar examenes reales cuando la lectura automatica no resuelve examen, estudiante o respuestas con suficiente certeza.
- Para permitir ajuste fino de umbrales segun calidad de captura sin tocar codigo cada vez.
- Para dar herramientas visuales de auditoria sobre ratios y overlay directamente en el frontend web.

## Que problemas se presentaron
- Los intentos anteriores no tenian `aligned_image_path` disponible en trace json, lo que impedia abrir el overlay aun con una lectura nueva aparentemente valida.
- El selector de estudiante no escalaba bien cuando el volumen de estudiantes aumentaba.
- La correccion de `resolution_error` exigia demasiada friccion operativa si no se podia reasignar manualmente examen y estudiante.

## Como se resolvieron
- Se uso un fallback en backend para reconstruir la ruta alineada a partir del `uploaded_image_path` y el sufijo `.aligned.jpg`.
- Se introdujeron endpoints runtime para umbrales y se consumieron desde la pestaña de examenes calificados con guardado al salir del campo.
- Se agregaron vistas especializadas en frontend para ratios y overlay, reutilizando artefactos ya generados por el pipeline OMR.
- Se cambio el control de estudiante a autocompletado para mantener `student_id` sincronizado sin obligar al usuario a recorrer listas extensas.
- Se agrego reasignacion manual de examen/version/estudiante usando datos ya leidos del intento y recalcificando contra la version seleccionada.

## Que continua
- Validar con mas intentos reales si los umbrales runtime convergen a un rango estable segun resolucion e iluminacion.
- Evaluar si los ratios y overlay deben persistirse tambien en base de datos o si los artefactos en disco son suficientes.
- Registrar una bitacora adicional cuando se consoliden pruebas con examenes reales y se definan umbrales operativos recomendados.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
