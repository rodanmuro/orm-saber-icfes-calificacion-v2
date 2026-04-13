# Bitacora 061_04_13_2026 15:55:00 integracion_calificacion_examenes_omr

## Que fue lo que se hizo
- Se integro la calificacion por version de examen: el backend ahora acepta `exam_id` y `exam_version_id` desde la app movil y, cuando no se envia version, resuelve automaticamente la ultima version publicada asociada al codigo de examen detectado en la hoja.
- Se agrego el listado de intentos OMR y detalle de respuestas para mostrarlos en el frontend web dentro de la nueva pestaña "Examenes calificados".
- Se ajusto el guardado del intento OMR para vincularlo con `exam_version_id` y `student_id` en base de datos.
- Se corrigio la ruta de imagenes de intentos para que el modal de imagen renderice correctamente el archivo real.
- Se ajusto la compresion de imagen en la app movil a 900px y 0.5 para reducir peso de envio.
- Archivos backend modificados/creados: `src/backend/app/api/v1/endpoints/omr_read.py`, `src/backend/app/db/models.py`, `src/backend/app/modules/omr_scoring/persistence.py`, `src/backend/app/modules/omr_scoring/service.py`, `src/backend/alembic/versions/20260413_0004_add_exam_version_student_to_omr_attempt.py`.
- Archivos frontend web modificados/creados: `src/frontend_web/src/App.jsx`, `src/frontend_web/src/styles.css`, `src/frontend_web/src/api/omrApi.js`, `src/frontend_web/src/components/AttemptList.jsx`.
- Archivos app movil modificados/creados: `src/frontend/App.js`, `src/frontend/src/services/omrRead.js`, `src/frontend/src/services/exams.js`.

## Para que se hizo
- Para calificar examenes contra la version correcta (con preguntas y opciones barajadas) sin pedir al usuario ingresar manualmente el id de version.
- Para visualizar en la web los examenes calificados, con detalle de respuestas, estado y evidencia fotografica.
- Para reducir el peso de las fotos enviadas desde el movil y mejorar tiempos de subida.

## Que problemas se presentaron
- La imagen del examen calificado no se mostraba en el modal; solo aparecia el texto alternativo.
- El peso de las fotos desde el movil era alto para el envio por red.

## Como se resolvieron
- Se normalizo la ruta de la imagen devuelta por backend para mapearla correctamente a `/assets/...` y permitir que el frontend renderice el archivo en el modal.
- Se implemento compresion y redimensionamiento en la app movil (900px, calidad 0.5) para reducir el peso sin perder legibilidad para OMR.

## Que continua
- Ejecutar la migracion `20260413_0004_add_exam_version_student_to_omr_attempt.py` en el entorno local.
- Probar end-to-end la calificacion por version desde movil y validar que la lista de examenes calificados se refresque correctamente.
- Ajustar los iconos de correct/incorrect/blank en el detalle para una lectura rapida.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
