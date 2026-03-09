# Bitacora 030_03_09_2026 11:15:08 avance_act_0033_frontend_web

## Que fue lo que se hizo
- Se inicio la implementacion de `ACT_0033` (frontend web base para CRUD de items).
- Se creo `src/frontend_web` con base Vite + React y estructura inicial:
  - `src/frontend_web/package.json`
  - `src/frontend_web/index.html`
  - `src/frontend_web/vite.config.js`
  - `src/frontend_web/.env.example`
  - `src/frontend_web/src/App.jsx`
  - `src/frontend_web/src/main.jsx`
  - `src/frontend_web/src/styles.css`
  - `src/frontend_web/src/api/itemsApi.js`
  - `src/frontend_web/src/components/ItemForm.jsx`
  - `src/frontend_web/src/components/ItemList.jsx`
  - `src/frontend_web/src/components/FiltersBar.jsx`
  - `src/frontend_web/README.md`
- Se agrego soporte backend para edicion de items via `PUT /api/v1/items/{item_id}`:
  - `src/backend/app/api/v1/endpoints/items.py`
  - `src/backend/app/schemas/item_bank.py` (`ItemUpdate`)
  - Ajustes de pruebas en `src/backend/tests/test_items_api.py` y `src/backend/tests/test_items_integration.py`.
- Se habilito CORS para frontend web local:
  - `src/backend/app/main.py` (`CORSMiddleware`)
  - `src/backend/app/core/config.py` (`cors_allowed_origins`).
- Se normalizo el flujo de ejecucion backend con script:
  - `src/backend/run-app.sh`.
- Se reorganizo entorno virtual para ruta unica en backend y se ajustaron guias:
  - `README.md`
  - `src/backend/README.md`
  - `src/frontend/README.md`
  - `.gitignore` (ignorar `src/backend/.venv*`).

## Para que se hizo
- Entregar un primer frontend web funcional para gestion de items sin depender de frontend movil.
- Completar el flujo HU_005 en modo base: crear, listar, consultar y editar items.
- Evitar friccion operativa dejando una unica ruta oficial de entorno virtual (`src/backend/.venv`).

## Que problemas se presentaron
- El frontend web recibio `405 Method Not Allowed` en preflight `OPTIONS` por falta de CORS en backend.
- Al mover el entorno virtual a `src/backend/.venv`, el entorno previo quedo inconsistente (rutas internas rotas), generando `ModuleNotFoundError: sqlalchemy` y luego fallas de ejecutables.
- En ejecuciones del agente, hubo cuelgues intermitentes al entrar a `TestClient` en pruebas de items.
- Al reinstalar dependencias aparecieron warnings de conflictos de paquetes de otros stacks (ej. `tensorflow`, `htmx`) en el entorno contaminado.

## Como se resolvieron
- Se agrego `CORSMiddleware` con origenes configurables desde settings para permitir frontend Vite local.
- Se definio `run-app.sh` con validacion explicita de `src/backend/.venv` y mensaje de recuperacion si no existe.
- Se establecio politica de ruta unica del venv en docs (`src/backend/.venv`) y se elimino el symlink temporal de raiz.
- Se agrego regla de ignore para backups de venv (`src/backend/.venv*`).
- Se dejo recomendado recrear venv limpio en backend cuando existan conflictos heredados de paquetes externos.

## Que continua
- Validar manualmente en UI todo el flujo CRUD de items (crear, listar, consultar, editar, filtros).
- Cerrar formalmente `ACT_0033` en `DONE` con evidencia de pruebas manuales/automáticas.
- Crear bitacora de cierre de `ACT_0033` y luego ejecutar `git add`, `commit` y `push`.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
