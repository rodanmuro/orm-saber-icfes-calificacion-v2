# Bitacora 040_03_13_2026 09:17:43 curriculum_backend_y_tools_postgres

## Que fue lo que se hizo
Se identificaron seis archivos sin commitear de trabajo previo (sesiones anteriores al 13/03/2026) y se registro su trazabilidad en planeacion.

### Bloque 1 — Curriculum backend (EP_002 / HU_005)
- Se creo `src/backend/app/api/v1/endpoints/curriculum.py` con dos endpoints:
  - `GET /curriculum/standards`: busqueda de estandares curriculares por texto, paginada con limite.
  - `GET /curriculum/competencies`: busqueda de competencias, filtrable por `standard_id` o `standard_code` y termino libre.
- Se creo `src/backend/app/schemas/curriculum.py` con schemas `StandardRefRead` y `CompetencyRefRead`.
- Se registro `curriculum_router` en `src/backend/app/api/v1/router.py`.
- Se extendio `CurriculumRef` en `src/backend/app/schemas/item_bank.py` agregando `standard_id` y `competency_id` para soportar resolucion directa por ID (antes solo habia `_code` y `_name`).

### Bloque 2 — Herramientas PostgreSQL (EP_004 / HU_011)
- Se creo `src/backend/run-app-postgres.sh`: script de arranque del backend con PostgreSQL, configurable via variables de entorno (`DATABASE_URL`, `HOST`, `PORT`, `RELOAD`). Valida existencia del entorno virtual antes de ejecutar uvicorn.
- Se creo `src/backend/scripts/migrate_sqlite_items_to_postgres.py`: script de migracion one-shot de items desde SQLite a PostgreSQL. Mapea docentes, estandares, competencias e items, evitando duplicados mediante firma de item (combinacion de campos clave). Es idempotente.

### Planeacion creada
- `ACT_0055_HU_05_EP_002_DONE.md` — curriculum backend y extension CurriculumRef.
- `ACT_0056_HU_11_EP_004_DONE.md` — run-app-postgres.sh y script de migracion.

## Para que se hizo
- Los endpoints de curriculum habilitan el autocompletado de estandares y competencias en el editor de items del frontend; sin ellos, el campo de etiquetado curricular no funcionaria.
- La extension de `CurriculumRef` con IDs permite que el backend resuelva la entidad directamente sin buscarla solo por codigo, reduciendo ambiguedad.
- El script de arranque estandariza como los desarrolladores levantan el backend contra PostgreSQL sin recordar el comando completo.
- El script de migracion permitio mover items creados originalmente en SQLite (entorno de desarrollo previo) hacia PostgreSQL sin perder datos y sin duplicarlos en corridas repetidas.

## Que problemas se presentaron
- Los seis archivos habian quedado sin commitear desde sesiones anteriores (entre el 11/03 y el 12/03/2026), sin actividad de planeacion asociada.
- No habia evidencia documental de cuando exactamente se crearon ni que actividad los origino.

## Como se resolvieron
- Se reviso el diff de los archivos modificados y el contenido de los archivos untracked.
- Se cruzo con las bitacoras 036 y 037 para confirmar que no estaban cubiertos por ACT_0043-0046.
- Se crearon las actividades faltantes (ACT_0055 y ACT_0056) marcadas como DONE.
- Se registro esta bitacora de cierre antes de commitear.

## Que continua
- Hacer commit y push de los seis archivos mas las actividades y esta bitacora.
- Revisar si ACT_0046 puede cerrarse formalmente (estado actual: in_progress).
- Continuar con ACT_0047 (validacion OMR sobre PostgreSQL) o ACT_0050/0051 (importacion GIFT).

*(Actividades de planeacion: ACT_0055_HU_05_EP_002_DONE.md, ACT_0056_HU_11_EP_004_DONE.md)*
