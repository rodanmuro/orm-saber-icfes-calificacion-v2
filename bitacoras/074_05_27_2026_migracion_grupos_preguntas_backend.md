# Bitacora 074_05_27_2026 09:18:27 migracion_grupos_preguntas_backend

## Que fue lo que se hizo
- Se implemento la primera fase backend para soportar agrupacion de preguntas asociadas dentro de un examen, agregando `group_key` en `exam_item`.
- Se creo la migracion Alembic `src/backend/alembic/versions/20260527_0009_add_group_key_to_exam_item.py`.
- Se actualizaron `src/backend/app/db/models.py`, `src/backend/app/schemas/exam_bank.py` y `src/backend/app/api/v1/endpoints/exams.py` para persistir, leer y actualizar `group_key`.
- Se agrego endpoint `PATCH /api/v1/exams/{exam_id}/items/{item_id}` para editar `group_key` de un item asociado.
- Se ajusto `src/backend/app/modules/exam_version/service.py` para que la publicacion de versiones baraje bloques de preguntas, manteniendo consecutivas las que comparten el mismo `group_key`.
- Se agregaron pruebas en `src/backend/tests/test_exam_version_service.py`, `src/backend/tests/test_exam_versions_api.py` y `src/backend/tests/test_exam_grouping_backend.py`.

## Para que se hizo
- Preparar la base de datos y la logica de backend para una futura interfaz donde el docente pueda marcar preguntas que deben permanecer seguidas aunque la version publicada se baraje.
- Mantener compatibilidad con produccion haciendo que `group_key = NULL` conserve el comportamiento historico.

## Que problemas se presentaron
- Las pruebas API con `TestClient` se colgaban dentro del sandbox, lo que hacia ambiguo si el problema era del cambio o del entorno de ejecucion.
- Era importante evitar mezclar este cambio con otros ajustes frontend ya presentes en el working tree para no perder un punto de reversa limpio.

## Como se resolvieron
- Se valido la logica principal con pruebas ejecutables en sandbox: `test_exam_version_service.py` y `test_exam_grouping_backend.py`.
- Se ejecuto con permisos escalados la prueba HTTP puntual `tests/test_exam_versions_api.py::test_publish_exam_version_keeps_grouped_exam_items_together`, confirmando que el cuelgue venia del sandbox y no del codigo de agrupacion.
- Se dejo `group_key` como campo aditivo y nullable, sin modificar datos existentes ni versiones ya publicadas.
- Se decidio aislar este commit solo a la fase backend y sus pruebas, dejando fuera cambios no relacionados del frontend.

## Que continua
- Conectar `group_key` en `frontend_web`, especificamente en `Items asociados` dentro de `ExamBuilder`.
- Definir UX para editar el bloque por fila y guardar por `PATCH`.
- Ampliar pruebas end-to-end cuando se complete la integracion frontend-backend.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
