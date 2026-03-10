# Bitacora 033_03_09_2026 22:17:07 descripcion_detallada_base_datos

## Que fue lo que se hizo
- Se elaboro una descripcion tecnica detallada del estado actual del modelo de datos SQLite del backend (`src/backend/data/omr_app.db`).
- Se documentaron las tablas operativas vigentes:
  - `teacher`, `student`, `standard`, `competency`
  - `item`, `exam`, `exam_item`
  - `exam_version`, `exam_version_item`
  - `omr_attempt`, `omr_attempt_answer`
- Se explico el rol de cada entidad en el flujo completo: banco de preguntas, armado de examenes, versionado con barajado y registro de intentos OMR.
- Se registro como se guarda la respuesta correcta en tres niveles:
  - Base del item (`item.correct_answer`)
  - Orden de examen (`exam_item.order_position` + join a `item`)
  - Version barajada (`exam_version.answer_key_json` y `exam_version_item.correct_answer_mapped`)
- Se dejo explicito que el `exam_code` se almacena en `exam.exam_code` y que su unicidad es por docente (`teacher_id`, `exam_code`).
- Archivo creado:
  - `bitacoras/033_03_09_2026_descripcion_detallada_base_datos.md`

## Para que se hizo
- Para dejar trazabilidad formal de la arquitectura de datos actual antes de seguir con integracion E2E y pruebas funcionales.
- Para reducir ambiguedad sobre donde vive cada dato critico (pregunta, clave, version, intento y evidencia).
- Para alinear al equipo sobre la semantica de "item" (pregunta base) y "exam_version" (instancia barajada).

## Que problemas se presentaron
- Se detecto confusion funcional entre:
  - `exam_id` vs `exam_code`
  - `item.correct_answer` vs clave efectiva por version barajada
  - Tabla de examen base vs tablas de version
- Se presento incertidumbre sobre en que tabla consultar la clave correcta para distintos escenarios (sin barajado o con barajado).

## Como se resolvieron
- Se estructuro una explicacion por capas del modelo:
  - Capa banco: `item`
  - Capa examen: `exam` + `exam_item`
  - Capa version/publicacion: `exam_version` + `exam_version_item`
  - Capa evaluacion ejecutada: `omr_attempt` + `omr_attempt_answer`
- Se definio regla de lectura de respuestas correctas segun contexto:
  - Si no hay version publicada: usar orden de `exam_item` y `item.correct_answer`.
  - Si hay version barajada: usar `exam_version.answer_key_json` y validacion por `correct_answer_mapped`.
- Se consolido la ubicacion del identificador funcional del examen en `exam.exam_code`.

## Que continua
- Documentar en un anexo operativo consultas SQL recomendadas por caso de uso:
  - clave base del examen,
  - clave por version,
  - historial de intentos y respuestas del intento.
- Integrar esta documentacion con actividades de integracion total EP_003 (calificacion por docente + version).
- Definir y documentar criterio de seleccion de clave al momento de calificar OMR cuando exista version publicada.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
