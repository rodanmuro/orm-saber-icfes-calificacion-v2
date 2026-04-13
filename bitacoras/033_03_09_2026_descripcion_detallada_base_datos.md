# Bitacora 033_03_09_2026 22:17:07 descripcion_detallada_base_datos

## Que fue lo que se hizo
- Se elaboro una descripcion tecnica detallada del estado actual del modelo de datos SQLite del backend (`src/backend/data/omr_app.db`).
- Se identificaron y explicaron las tablas operativas vigentes:
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
- Actualizar este documento cuando se agreguen nuevos campos estructurales relevantes (por ejemplo, datos de estudiante y grupo).

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*

## Anexo explicativo (lenguaje no tecnico)

Este sistema guarda la informacion en varios bloques que trabajan juntos, como si fueran carpetas relacionadas:

- **Docentes** (`teacher`): aqui se guarda quien crea los examenes.
- **Estudiantes** (`student`): aqui se guarda la identificacion base del estudiante.
- **Preguntas** (`item`): aqui se guarda cada pregunta con sus opciones y su respuesta correcta.
- **Examenes** (`exam`): un examen no copia preguntas nuevas; mas bien selecciona preguntas ya existentes y las ordena.
- **Relacion examen-pregunta** (`exam_item`): define que preguntas van en cada examen y en que posicion.
- **Versiones del examen** (`exam_version`): una version es una presentacion concreta del examen, donde se puede cambiar el orden de preguntas y tambien el orden de opciones para evitar copia.
- **Detalle por pregunta de una version** (`exam_version_item`): guarda para cada pregunta como quedaron las opciones y cual es la correcta final de esa version.
- **Intentos de lectura OMR** (`omr_attempt`): cada vez que se toma una foto y se califica, se guarda un registro del intento con el resultado.
- **Detalle de respuestas leidas en un intento** (`omr_attempt_answer`): guarda el resultado por pregunta dentro del intento.
- **Estandares curriculares** (`standard`) y **competencias** (`competency`): catalogos para clasificar preguntas por referente pedagogico.

### Como se relacionan entre si

- Un docente (`teacher`) puede crear muchas preguntas (`item`).
- Un docente (`teacher`) puede crear muchos examenes (`exam`).
- Un examen (`exam`) se arma uniendo varias preguntas mediante `exam_item` (alli se guarda el orden).
- Una pregunta (`item`) puede aparecer en muchos examenes distintos.
- Un examen (`exam`) puede tener varias versiones (`exam_version`), por ejemplo V001, V002.
- Cada version (`exam_version`) tiene su detalle por pregunta en `exam_version_item`.
- Cada intento OMR (`omr_attempt`) puede vincularse con un docente y un examen, y tiene sus respuestas por pregunta en `omr_attempt_answer`.
- Una pregunta (`item`) puede vincularse opcionalmente a un estandar (`standard`) y a una competencia (`competency`).
- Cada estudiante (`student`) ahora tambien tiene un **grupo** (`group_name`) para clasificacion escolar interna.

### Donde vive la respuesta correcta

La respuesta correcta existe en tres niveles, porque cada nivel cumple un objetivo distinto:

1. **Pregunta base** (`item`): la correcta original de la pregunta.
2. **Examen en orden base** (`exam` + `exam_item`): la correcta de cada pregunta segun el orden en que fue armada.
3. **Version barajada** (`exam_version` + `exam_version_item`): la correcta final despues de mezclar opciones, que es la que realmente se usa para calificar esa version.

En palabras simples: la pregunta original tiene una correcta, pero si se cambian las opciones para una version, la letra correcta puede cambiar para esa version.

### Como se guardan las opciones de una pregunta

- En `item.options` se guarda un **JSON** con las opciones A, B, C y D.
- En `item.correct_answer` se guarda la letra correcta original (por ejemplo, `B`).
- Cuando una version cambia el orden de opciones:
  - `exam_version_item.option_map_json` guarda el mapeo de letras originales a letras nuevas.
  - `exam_version_item.correct_answer_original` guarda la letra correcta antes del cambio.
  - `exam_version_item.correct_answer_mapped` guarda la letra correcta despues del cambio.
  - `exam_version.answer_key_json` guarda la clave final completa de esa version.

### Identificador del examen

- El codigo que identifica el examen para operar en el flujo (`exam_code`) se guarda en la entidad de examenes.
- Ese codigo se interpreta junto con el docente, para evitar choques entre examenes de docentes diferentes.

### Grupo del estudiante (nuevo)

- Se agrego `student.group_name` como texto corto **obligatorio** para registrar el grupo del estudiante.
- Este dato alimenta el tablero de **Examenes calificados** y permite filtrar resultados por grupo.

---

## Enmienda — 2026-03-15 (ver bitacora 041)

Los campos `code` en las tablas `standard` y `competency` fueron **eliminados** en la sesion del 15 de marzo de 2026. Lo descrito arriba refleja el estado original; el estado vigente es el siguiente:

### Cambios en el modelo de datos

| Tabla | Campo eliminado | Nueva unicidad |
|---|---|---|
| `standard` | `code VARCHAR(64) UNIQUE` | `UNIQUE(name)` |
| `competency` | `code VARCHAR(64)`, constraint `uq_competency_standard_code` | `UNIQUE(standard_id, name)` |

- El campo `code` era redundante frente al `id` (PK autoincrement) y no aportaba semantica adicional en este proyecto.
- La migracion `20260315_0002_drop_code_use_name_as_identifier.py` aplica estos cambios en Postgres.

### Cambios en el schema de API

- `CurriculumRef` ya no tiene `standard_id`, `standard_code`, `competency_id`, `competency_code`.
- El cliente solo envia `{ standard_name, competency_name }`.
- El backend hace `get_or_create` por `name` (standard) y por `(standard_id, name)` (competency).

### Cambios en el frontend

- El formulario de item muestra solo los campos **Estandar** (nombre) y **Competencia** (nombre).
- El listado de items muestra columnas **Estandar** y **Competencia** en lugar de "Curricular".
