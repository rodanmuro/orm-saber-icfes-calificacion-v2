estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0033 - Frontend web base para CRUD de items

## Objetivo tecnico
Crear el frontend web inicial para que el docente gestione preguntas del banco de items con operaciones CRUD y filtros basicos.

## Tareas implementables
- [x] Inicializar `src/frontend_web` con estructura de proyecto y configuracion base.
- [x] Implementar pantallas de listado y formulario de item.
- [x] Integrar consumo de API backend para crear, editar, listar y consultar items.
- [x] Implementar filtros basicos por area, dificultad y etiqueta curricular.
- [x] Validar flujo completo UI -> API -> persistencia para banco de items.

## Evidencias esperadas
- Frontend web ejecutable en entorno local.
- Flujo de CRUD funcional sobre items.
- Evidencia visual de filtros y formulario de creacion/edicion.

## Criterio de terminado
Un docente puede gestionar items desde la interfaz web sin depender del frontend movil.

## Evidencia de cierre
- Frontend web inicial implementado en `src/frontend_web`:
  - `src/frontend_web/src/App.jsx`
  - `src/frontend_web/src/components/ItemForm.jsx`
  - `src/frontend_web/src/components/ItemList.jsx`
  - `src/frontend_web/src/components/FiltersBar.jsx`
  - `src/frontend_web/src/api/itemsApi.js`
- Consumo de API CRUD sobre items:
  - `POST /api/v1/items`
  - `GET /api/v1/items`
  - `GET /api/v1/items/{id}`
  - `PUT /api/v1/items/{id}` (agregado para soportar edicion en UI).
- Build frontend validado:
  - `cd src/frontend_web && npm run build` -> `✓ built`.
- Validacion manual en UI realizada:
  - carga de listado de items,
  - render de formulario,
  - accion `Consultar / Editar`,
  - filtros visibles por area/dificultad/etiqueta curricular.
