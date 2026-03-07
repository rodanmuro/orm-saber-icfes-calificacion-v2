# Bitacora 029_03_06_2026 19:18:02 cierre_act_0032_items_backend

## Que fue lo que se hizo
- Se implemento la base del modulo de banco de items en backend (ACT_0032) con SQLAlchemy y SQLite.
- Se agrego `SQLAlchemy==2.0.43` en `src/backend/requirements.txt`.
- Se creo la capa DB en `src/backend/app/db/`:
  - `base.py` (DeclarativeBase)
  - `models.py` (teacher, student, standard, competency, item)
  - `session.py` (engine, SessionLocal, get_db)
  - `init_db.py` (create_all)
- Se expusieron endpoints de items en `src/backend/app/api/v1/endpoints/items.py`:
  - `POST /api/v1/items`
  - `GET /api/v1/items`
  - `GET /api/v1/items/{item_id}`
- Se registraron rutas en `src/backend/app/api/v1/router.py`.
- Se agregaron DTOs/validaciones en `src/backend/app/schemas/item_bank.py`:
  - opciones exactamente A/B/C/D
  - `correct_answer` coherente con opciones
  - campos curriculares lite opcionales.
- Se versiono migracion inicial en `src/backend/migrations/0001_initial_item_bank.sql`.
- Se migro `startup` de FastAPI a `lifespan` en `src/backend/app/main.py` para eliminar warning deprecado de `on_event`.
- Se cerro actividad moviendo y actualizando `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0032_HU_05_EP_002_DONE.md`.

## Para que se hizo
- Habilitar persistencia y consulta de items en backend como base del banco de preguntas.
- Dejar un slice funcional y validable antes de iniciar frontend web (ACT_0033).
- Reducir deuda tecnica inmediata eliminando el uso de `@app.on_event("startup")`.

## Que problemas se presentaron
- Al inicio no estaba instalado SQLAlchemy en el entorno virtual.
- Hubo ejecuciones de prueba con bloqueo intermitente al usar `TestClient` en este entorno de agente.
- Aparecio warning de FastAPI por deprecacion de `on_event`.

## Como se resolvieron
- Se instalaron dependencias actualizadas del backend (`pip install -r src/backend/requirements.txt`).
- Se adiciono test de integracion dedicado `src/backend/tests/test_items_integration.py` para validar flujo HTTP completo de items.
- El usuario valido ejecucion manual de pruebas en consola:
  - `tests/test_items_api.py` -> `2 passed`
  - `tests/test_items_integration.py` -> `1 passed`
- Se reemplazo `on_event` por `lifespan` en `app/main.py`, eliminando warning de FastAPI.

## Que continua
- Iniciar `ACT_0033` (frontend web base para CRUD de items).
- Definir primer flujo UI -> API para crear/listar items usando endpoints ya disponibles.
- Revisar warnings deprecados restantes de Pydantic en modulos legacy (no bloqueantes para ACT_0032).

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
