# Bitacora 064_04_28_2026 11:04:20 ajustes_examenes_calificados_versiones

## Que fue lo que se hizo
- Se revisaron y consolidaron cambios de frontend en la tabla de `Examenes calificados` para seleccion y borrado:
  - Checkboxes por fila y seleccion total visible.
  - Boton de borrado individual y borrado masivo.
  - Estados de UI durante borrado (`Borrando...`).
- Se confirmo la alineacion frontend-backend para borrado de intentos OMR usando `DELETE /omr/attempts/{attempt_id}`.
- Se ajusto el modelo y flujo de versiones de examen para que la identificacion OMR sea por version:
  - `exam_version` con `teacher_id` y `exam_code` unico por docente.
  - Normalizacion de `version_code` a formato numerico (`1`, `2`, ...), reemplazando `V001`, `V002`.
- Se movio la exportacion a un flujo por version publicada (PDF/DOCX por fila de version).
- Se corrigio el render en exportacion:
  - PDF: ajuste de ancho efectivo para tablas dentro de columnas.
  - DOCX: tabla con ancho fijo y `autofit` deshabilitado para reducir desbordes.
  - DOCX: reduccion de espaciado tras encabezado `Pregunta X` para ahorro de paginas.
- Se ampliaron columnas de `Examenes calificados`:
  - `Total`, `Correctas`, `Incorrectas`, `No marcadas`.
  - Backend de listados devuelve `total_questions`, `correct_count`, `incorrect_count`, `blank_count`.
- Archivos modificados principales:
  - `src/frontend_web/src/components/AttemptList.jsx`
  - `src/frontend_web/src/App.jsx`
  - `src/frontend_web/src/api/omrApi.js`
  - `src/frontend_web/src/styles.css`
  - `src/backend/app/api/v1/endpoints/omr_read.py`
  - `src/backend/app/api/v1/endpoints/exams.py`
  - `src/backend/app/modules/exam_export/pdf_service.py`
  - `src/backend/app/modules/exam_export/docx_service.py`
  - `src/backend/app/db/models.py`
  - `src/backend/app/schemas/exam_bank.py`
- Archivos creados de migracion:
  - `src/backend/alembic/versions/20260416_0006_add_exam_code_to_exam_version.py`
  - `src/backend/alembic/versions/20260416_0007_normalize_exam_version_code_numeric.py`

## Para que se hizo
- Permitir operacion mas eficiente del docente en la bandeja de examenes calificados (gestion de volumen y limpieza de intentos).
- Alinear el identificador OMR con la version real del examen impreso para evitar ambiguedad de clave de respuestas.
- Mejorar calidad de salida de cuadernillos exportados y reducir uso de hojas en impresion.
- Dar trazabilidad rapida en la tabla con metricas clave por intento.

## Que problemas se presentaron
- El frontend mostraba `V001/V002` aunque la base ya estaba en `1/2`.
- Se detecto mezcla de estados de despliegue (bundle/backend desincronizado) durante pruebas manuales.
- En exportacion, algunas tablas quedaban visualmente desbordadas en PDF/DOCX.
- En DOCX habia espacio innecesario tras `Pregunta X`, aumentando paginacion.

## Como se resolvieron
- Se normalizo `version_code` en backend y en datos existentes con migracion `0007`.
- Se verifico estado de migraciones en DB (`alembic_version = 20260416_0007`) y datos de `exam_version` (`1`, `2`).
- Se actualizo frontend para publicar/exportar por version y mostrar valores normalizados.
- Se ajusto el renderer PDF para calcular ancho de contenido por celda de tabla, no por columna completa.
- Se ajusto el renderer DOCX para fijar anchos de tabla/celda y deshabilitar `autofit`.
- Se aplico `_no_spacing` al encabezado de pregunta para compactar layout.
- Se extendio `GET /omr/attempts` con campos de conteo para alimentar columnas nuevas del frontend.

## Que continua
- Ejecutar prueba funcional completa de `Examenes calificados` con borrado individual y masivo en entorno real.
- Validar en varios cuadernillos que tablas en DOCX/PDF no desborden en casos extremos.
- Evaluar eliminacion de `exam.exam_code` del modelo base si se decide consolidar totalmente el codigo en `exam_version`.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
