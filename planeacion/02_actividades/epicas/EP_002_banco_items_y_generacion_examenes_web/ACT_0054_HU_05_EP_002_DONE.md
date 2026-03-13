estado: done
prioridad: alta
sprint: S6
owner: por_definir

# ACT_0054 - Borrar item, renombrar boton guardar y navegacion prev/next en editor web

## Objetivo tecnico
Completar el CRUD de items en el frontend web agregando borrado, unificar el texto del boton de guardado y habilitar navegacion secuencial entre items desde la pantalla de edicion.

## Tareas implementables
- [x] Agregar endpoint `DELETE /items/{item_id}` en el backend (`items.py`). Retorna `Response(204)` para compatibilidad con la version de FastAPI instalada.
- [x] Agregar funcion `deleteItem(itemId)` en `itemsApi.js` con manejo correcto de respuesta 204 (sin body).
- [x] Renombrar boton de submit a "Guardar item" tanto en modo crear como en modo editar (antes decia "Crear item" / "Actualizar item").
- [x] Agregar boton "Borrar item" (estilo danger) visible solo en modo edicion, con confirmacion via `window.confirm` antes de ejecutar el borrado.
- [x] Agregar flechas de navegacion `←` / `→` junto al titulo del formulario, visibles solo en modo edicion. Deshabilitadas en los extremos del array de items.
- [x] Agregar estilos `.item-form-header`, `.nav-btn`, `.btn-danger` en `styles.css` con fondo azul oscuro (#4a6fa5) y flecha blanca para contraste adecuado.
- [x] Cablear `handleDeleteItem` y `handleNavigate` en `App.jsx` y pasar los props `hasPrev`, `hasNext` calculados desde el array `items`.

## Archivos modificados
- `src/backend/app/api/v1/endpoints/items.py`
- `src/frontend_web/src/api/itemsApi.js`
- `src/frontend_web/src/components/ItemForm.jsx`
- `src/frontend_web/src/App.jsx`
- `src/frontend_web/src/styles.css`

## Evidencias esperadas
- `DELETE /items/{id}` responde 204 y elimina el registro de la base de datos.
- El boton de submit siempre dice "Guardar item".
- El boton "Borrar item" aparece solo al editar un item existente y solicita confirmacion antes de borrar.
- Las flechas `←` / `→` permiten navegar entre items sin volver al listado; se deshabilitan en los extremos.

## Criterio de terminado
El docente puede borrar un item directamente desde el formulario de edicion y navegar al anterior o siguiente item sin salir de la pantalla de edicion.
