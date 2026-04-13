# Bitacora 062_04_13_2026 16:27:26 correccion_manual_filtros_omr

## Que fue lo que se hizo
- Se implemento la correccion manual de respuestas OMR con guardado automatico al cambiar el selector en el modal de "Examenes calificados".
- Se agrego soporte backend para overrides manuales en cada respuesta (campos `manual_answer` y `manual_override`) y recalculo de puntajes basado en la respuesta efectiva.
- Se agregaron filtros en la tabla de examenes calificados (busqueda, estado y grupo).
- Archivos backend modificados/creados: `src/backend/app/api/v1/endpoints/omr_read.py`, `src/backend/app/db/models.py`, `src/backend/app/modules/omr_scoring/persistence.py`, `src/backend/alembic/versions/20260413_0005_add_manual_override_omr_attempt_answer.py`.
- Archivos frontend web modificados: `src/frontend_web/src/App.jsx`, `src/frontend_web/src/components/AttemptList.jsx`, `src/frontend_web/src/api/omrApi.js`, `src/frontend_web/src/styles.css`.

## Para que se hizo
- Para permitir correccion manual inmediata y evitar perdida de cambios por cierre accidental del modal.
- Para reflejar con claridad los casos de respuestas ambiguas y ajustes manuales en el puntaje final.
- Para encontrar rapidamente intentos por estudiante, examen o estado.

## Que problemas se presentaron
- Riesgo de perder correcciones si no se presionaba el boton de guardar.

## Como se resolvieron
- Se cambio el flujo para guardar automaticamente al modificar el selector, manteniendo un boton de respaldo para reintentos.
- Se agrego un endpoint PATCH que actualiza overrides y recalcula el resumen del intento.

## Que continua
- Validar el flujo end-to-end con un intento real y confirmar que el refresco de la lista mantiene los filtros aplicados.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
