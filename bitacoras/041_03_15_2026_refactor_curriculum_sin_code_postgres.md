# Bitacora 041_03_15_2026 15:24:45 refactor_curriculum_sin_code_postgres

## Que fue lo que se hizo

### Eliminación del campo `code` en `standard` y `competency`
- Se tomó la decisión de eliminar el campo `code` de las tablas `standard` y `competency`, ya que era redundante frente al `id` (PK autoincrement) y generaba complejidad innecesaria en el cliente.
- Se creó una nueva migración Alembic: `alembic/versions/20260315_0002_drop_code_use_name_as_identifier.py`
  - Drop de `ix_standard_code` (con `if_exists=True` para robustez en distintos dialectos)
  - Drop de columna `code` en `standard`
  - Drop de constraint `uq_competency_standard_code`
  - Drop de columna `code` en `competency`
  - Creación de `UNIQUE(name)` en `standard` y `UNIQUE(standard_id, name)` en `competency`

### Backend simplificado
- `app/db/models.py`: `Standard` y `Competency` sin campo `code`; unicidad por `name`.
- `app/schemas/curriculum.py`: `StandardRefRead` y `CompetencyRefRead` reducidos a `id` + `name`.
- `app/schemas/item_bank.py`: `CurriculumRef` simplificado a `standard_name` + `competency_name` (eliminados `standard_id`, `standard_code`, `competency_id`, `competency_code`).
- `app/api/v1/endpoints/curriculum.py`: endpoints de listado filtran y ordenan por `name`; eliminado query param `standard_code`.
- `app/api/v1/endpoints/items.py`: `_resolve_curriculum` reescrito — hace `get_or_create` por `name` tanto para standard como para competency. `_to_item_read` solo expone `standard_name` y `competency_name`.

### Frontend simplificado
- `ItemForm.jsx`: sección curricular reducida a 2 inputs — `Estandar` y `Competencia` (nombre libre con autocomplete). Se mantiene `_standard_id` como campo interno del form para filtrar competencias, no se envía al backend. El campo competencia se deshabilita si no hay standard seleccionado.
- `itemsApi.js`: `listCurriculumCompetencies` elimina el parámetro `standardCode`.
- `ItemList.jsx`: columna "Curricular" reemplazada por dos columnas "Estandar" y "Competencia" que muestran `standard_name` y `competency_name`.
- `App.jsx`: filtro `curricularTag` actualizado para buscar sobre `standard_name` + `competency_name`.

### Flechas de navegación en modo "Nuevo"
- `ItemForm.jsx`: las flechas anterior/siguiente se mostraban solo en `mode === 'edit'`. Se corrigió para que siempre sean visibles (deshabilitadas si no hay prev/next).

### Migración SQLite → PostgreSQL
- El backend apuntaba a SQLite por defecto; se agregó `DATABASE_URL` al `.env` apuntando a PostgreSQL local.
- Se detectó que SQLite tenía 58 ítems y PostgreSQL solo 52 (6 creados mientras el backend aún usaba SQLite).
- `scripts/migrate_sqlite_items_to_postgres.py` fue reescrito para usar SQL crudo al leer SQLite (ya que el modelo ORM no tiene `code`) y hacer `get_or_create` por `name` en PostgreSQL.
- Migración ejecutada exitosamente: 6 ítems creados, 52 skipped.

## Para que se hizo

- Simplificar el modelo de datos eliminando el campo `code` que no aportaba semántica adicional al `id`.
- Que el cliente (frontend) no tenga que gestionar identificadores internos (IDs, códigos).
- Unificar la BD activa en PostgreSQL para todo el equipo, evitando divergencia con SQLite.
- Mejorar la UX del editor de ítems con las flechas siempre visibles y columnas más claras en el listado.

## Que problemas se presentaron

- Al ejecutar `run-app.sh`, el backend intentaba correr la migración `20260315_0002` sobre SQLite, fallando con `no such index: ix_standard_code`. El script usa SQLite por defecto al no tener `DATABASE_URL` en el `.env`.
- La migración usaba `op.drop_index` sin `if_exists=True`, lo que la hacía frágil en SQLite.
- El script de migración SQLite→Postgres usaba `standard.code` y `competency.code` que ya no existen en el modelo ORM, causando error de atributo.

## Como se resolvieron

- Se agregó `DATABASE_URL=postgresql+psycopg://...` al `.env` para que `run-app.sh` use Postgres.
- Se añadió `if_exists=True` en los `op.drop_index` de la migración.
- El script `migrate_sqlite_items_to_postgres.py` fue reescrito para leer desde SQLite con SQL crudo (`text()`), evitando dependencia del modelo ORM que ya no tiene `code`.

## Que continua

- Verificar UX completa del formulario simplificado (estandar + competencia por nombre, autocomplete, creación implícita).
- Evaluar si el `FiltersBar` necesita actualizar el label del campo de filtro curricular.
- Crear actividad y actualizar historias de usuario para este refactor en la épica EP_002/EP_004.
- Hacer commit y push de todos los cambios de esta sesión.

## Enmienda realizada a bitacora anterior

- Se enmendo `bitacoras/033_03_09_2026_descripcion_detallada_base_datos.md` agregando una seccion de enmienda al final del documento.
- La enmienda deja constancia de que los campos `code` en `standard` y `competency` fueron eliminados, indica la nueva unicidad por `name`, los cambios en `CurriculumRef` y los cambios en el frontend.
- El contenido original de la bitacora 033 se preservo intacto; la enmienda se agrego como seccion separada al final.

*(Archivos clave: `alembic/versions/20260315_0002_...py`, `models.py`, `schemas/curriculum.py`, `schemas/item_bank.py`, `endpoints/curriculum.py`, `endpoints/items.py`, `ItemForm.jsx`, `ItemList.jsx`, `App.jsx`, `itemsApi.js`, `migrate_sqlite_items_to_postgres.py`, `.env`, `bitacoras/033_03_09_2026_descripcion_detallada_base_datos.md`)*
