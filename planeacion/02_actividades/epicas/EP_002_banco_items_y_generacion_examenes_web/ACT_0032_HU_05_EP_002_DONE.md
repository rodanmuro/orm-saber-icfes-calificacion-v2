estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0032 - Modelo backend base para banco de items y actores academicos

## Objetivo tecnico
Definir e implementar el modelo inicial de datos para docentes, estudiantes e items, habilitando persistencia estructurada y versionable para el banco de preguntas.

## Tareas implementables
- [x] Definir entidades base `teacher`, `student`, `item` y sus restricciones de unicidad.
- [x] Crear migraciones iniciales de base de datos para dichas entidades.
- [x] Exponer modelos/DTOs de lectura y escritura para items en backend.
- [x] Implementar validaciones minimas de consistencia de pregunta (opciones A/B/C/D + respuesta correcta).
- [x] Incluir campos curriculares basicos opcionales (estandar/competencia) en modo lite.

## Evidencias esperadas
- Migraciones aplicables en entorno local.
- Estructura de modelos en backend versionada en repositorio.
- Pruebas basicas de creacion y consulta de items.

## Criterio de terminado
El backend puede persistir y consultar items con estructura valida y metadatos curriculares basicos opcionales.

## Evidencia de cierre
- Modelado y capa DB implementados en `src/backend/app/db/`.
- Endpoints implementados en `src/backend/app/api/v1/endpoints/items.py` y registrados en `src/backend/app/api/v1/router.py`.
- DTOs y validaciones en `src/backend/app/schemas/item_bank.py`.
- Migracion SQL inicial en `src/backend/migrations/0001_initial_item_bank.sql`.
- Pruebas automaticas validadas manualmente por consola:
  - `DEBUG=false pytest -vv -s tests/test_items_api.py` -> `2 passed`
  - `DEBUG=false pytest -vv -s tests/test_items_integration.py` -> `1 passed`
