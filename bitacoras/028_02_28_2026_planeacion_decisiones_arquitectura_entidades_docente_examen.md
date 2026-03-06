# Bitacora 028_02_28_2026 11:03:12 decisiones_arquitectura_entidades_docente_examen

## Que fue lo que se hizo
- Se tomaron decisiones de planeacion y arquitectura para la siguiente fase del proyecto, sin implementar codigo funcional adicional en esta sesion.
- Se definio separar clientes frontend por contexto de uso:
  - `src/frontend_mobile` para captura y lectura OMR en campo.
  - `src/frontend_web` para creacion de preguntas, banco de items y armado de examenes.
- Se ratifico mantener backend en Python + FastAPI como API unica para ambos frontends.
- Se definio que un examen no es entidad suelta: debe estar asociado a un docente.
- Se establecio clave de negocio para examen basada en contexto docente:
  - `teacher_id + exam_code` (codigo OMR del examen en hoja).
- Se delimito el alcance de modelado para fase inicial:
  - usuarios/docentes,
  - estudiantes con UUID,
  - items/preguntas,
  - examenes,
  - versiones de examen,
  - intentos de lectura OMR,
  - artefactos y resultados.

## Para que se hizo
- Reducir ambiguedad antes de entrar a epicas, historias de usuario y actividades de implementacion.
- Asegurar que el diseno de datos soporte variaciones de examen (incluida reorganizacion aleatoria de respuestas).
- Evitar colisiones de identificacion de examen entre docentes cuando se usa un espacio limitado de codigos OMR.

## Que problemas se presentaron
- Riesgo de modelar examen como identificador global sin contexto de docente.
- Riesgo de mezclar responsabilidades de captura movil y authoring web en una sola app frontend.
- Necesidad de dejar claras las bases de integracion entre banco de items y motor OMR antes de implementar.

## Como se resolvieron
- Se adopto separacion arquitectonica por producto cliente (mobile vs web) con backend compartido.
- Se definio ownership explicito de examen por docente y clave compuesta de negocio.
- Se establecio el principio de versionado de examen para congelar orden y clave de calificacion al momento de aplicacion.
- Se alinearon decisiones con el documento fundacional y con la ruta de trabajo ya registrada en planeacion/bitacoras.
- Se aprobo estrategia incremental para el componente curricular del banco de preguntas:
  - **Now-lite**: agregar en `item` referencias opcionales a estándar/competencia y filtros básicos.
  - **Later-full**: incorporar familias de ítems/variantes parametrizables y cobertura curricular avanzada.

## Entidades y relaciones acordadas (modelo conceptual)
- `teacher`
  - Campos base: `id (UUID)`, `email`, `nombres`, `apellidos`, `estado`, timestamps.
  - Regla: `email` unico.
- `student`
  - Campos base: `id (UUID)`, `document_type`, `document_number`, `email`, `nombres`, `apellidos`, timestamps.
  - Regla: unicidad compuesta `document_type + document_number`.
- `item` (pregunta del banco)
  - Campos base: `id (UUID)`, `statement_json`, `options_json (A/B/C/D)`, `correct_answer`, `metadata_json`, `status`, `version`.
  - Ajuste curricular lite: `standard_id` y `competency_id` opcionales para etiquetado inicial.
- `standard` (catalogo curricular)
  - Campos base: `id`, `codigo`, `nombre`, `area`, `nivel`.
  - Uso: referencia curricular de alto nivel para clasificar preguntas.
- `competency` (catalogo de competencias)
  - Campos base: `id`, `standard_id (FK)`, `codigo`, `nombre`.
  - Uso: granularidad curricular asociada al estándar.
- `exam`
  - Campos base: `id (UUID interno)`, `teacher_id (FK)`, `exam_code (OMR)`, `name`, `subject`, `status`, timestamps.
  - Regla de negocio: examen identificado por `teacher_id + exam_code`.
  - Restriccion: `UNIQUE(teacher_id, exam_code)`.
- `exam_item`
  - Relacion N:M entre `exam` e `item`.
  - Campos base: `exam_id`, `item_id`, `position`.
- `exam_version`
  - Campos base: `id (UUID)`, `exam_id (FK)`, `version_number`, `seed_shuffle`, `is_published`, `created_at`.
  - Uso: snapshot inmutable de aplicacion/calificacion.
- `exam_version_item`
  - Campos base: `exam_version_id`, `item_id`, `question_number`, `option_map`, `correct_answer_mapped`.
  - Uso: representa orden final y remapeo de opciones por version.
- `omr_attempt`
  - Campos base: `id (UUID)`, `exam_version_id (FK)`, `student_id (FK nullable)`, `document_type_detected`, `document_number_detected`, `exam_identifier_detected`, `score`, `status`, timestamps.
  - Uso: intento de calificacion de una hoja concreta.
- `omr_attempt_answer`
  - Campos base: `attempt_id`, `question_number`, `marked_option`, `is_correct`, `ambiguous_options`, `ratios`.
- `omr_attempt_artifact`
  - Campos base: `id`, `attempt_id`, `artifact_type`, `storage_url`, `checksum`, timestamps.
  - Uso: trazabilidad de imagen original y salidas (`result.json`, `ratios.csv`, etc).

### Relaciones principales
- `teacher 1:N exam`
- `standard 1:N competency`
- `competency 1:N item` (modo lite, asociacion opcional en esta fase)
- `exam N:M item` (via `exam_item`)
- `exam 1:N exam_version`
- `exam_version 1:N exam_version_item`
- `exam_version 1:N omr_attempt`
- `student 1:N omr_attempt` (nullable al inicio si no se resuelve identidad)
- `omr_attempt 1:N omr_attempt_answer`
- `omr_attempt 1:N omr_attempt_artifact`

### Contratos de integracion definidos a nivel de dominio
- La calificacion OMR se realiza contra una `exam_version` publicada, nunca contra examen editable.
- El `exam_identifier` leido en hoja se resuelve en contexto de docente (`teacher_id + exam_code`).
- El mapeo de respuesta correcta depende de `exam_version_item.option_map`.
- En banco de preguntas, el etiquetado curricular se implementa primero en modo liviano (campos opcionales), dejando variantes/familias para siguiente incremento.
- Se incorpora estructura curricular base para clasificacion de items:
  - `standard -> competency -> item (opcional en fase lite)`.

## Decisiones tecnologicas base (acordadas en planeacion)
- Base de datos principal:
  - **PostgreSQL** para persistencia transaccional de entidades academicas, examenes versionados e intentos OMR.
- Almacenamiento de evidencias y assets:
  - **S3-compatible / MinIO** para imagenes de intentos, artefactos de trazabilidad y recursos multimedia.
- Editor de preguntas y opciones (frontend web):
  - **Tiptap** como editor estructurado para enunciado y opciones A/B/C/D.
  - Soporte de ecuaciones mediante **KaTeX** (LaTeX como fuente).

### Notas de alcance de estas decisiones
- Estas decisiones son base para los siguientes incrementos; no implican implementacion completa en esta bitacora.
- Se mantiene el enfoque incremental: primero capacidad funcional minima, luego ampliaciones de variantes/familias y analitica curricular avanzada.

## Que continua
- Traducir estas decisiones en epicas, historias de usuario y actividades concretas.
- Definir contrato tecnico entre modulo de banco de items y modulo OMR (mapeo de respuestas correctas y orden por version de examen).
- Diseñar esquema inicial de base de datos y endpoints para CRUD de items/examenes/versiones.
- Preparar fase de implementacion del frontend web de docente sin incluir autenticacion en este incremento.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
