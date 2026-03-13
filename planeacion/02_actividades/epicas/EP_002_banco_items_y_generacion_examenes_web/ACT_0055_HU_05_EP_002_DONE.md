estado: done
prioridad: alta
sprint: S5
owner: por_definir

# ACT_0055 - Endpoints de curriculum backend y extension de CurriculumRef

## Objetivo tecnico
Implementar los endpoints backend `/curriculum/standards` y `/curriculum/competencies` y extender el schema `CurriculumRef` para soportar lookups por ID ademas de por codigo, habilitando el autocompletado de etiquetas curriculares en el editor de items.

## Tareas implementables
- [x] Crear `src/backend/app/api/v1/endpoints/curriculum.py` con endpoints:
  - `GET /curriculum/standards` — busqueda de estandares por texto, con limite configurable.
  - `GET /curriculum/competencies` — busqueda de competencias filtrada opcionalmente por `standard_id` o `standard_code` y termino de busqueda.
- [x] Crear `src/backend/app/schemas/curriculum.py` con schemas `StandardRefRead` y `CompetencyRefRead`.
- [x] Registrar `curriculum_router` en `src/backend/app/api/v1/router.py`.
- [x] Extender `CurriculumRef` en `src/backend/app/schemas/item_bank.py` para incluir `standard_id` y `competency_id` (antes solo tenia los campos `_code` y `_name`), permitiendo resolucion directa por ID en el endpoint de items.

## Archivos creados/modificados
- `src/backend/app/api/v1/endpoints/curriculum.py` (nuevo)
- `src/backend/app/schemas/curriculum.py` (nuevo)
- `src/backend/app/api/v1/router.py` (modificado: registro del router)
- `src/backend/app/schemas/item_bank.py` (modificado: CurriculumRef ampliado)

## Evidencias esperadas
- `GET /api/v1/curriculum/standards?q=mat` retorna lista filtrada de estandares.
- `GET /api/v1/curriculum/competencies?standard_code=XXX` retorna competencias del estandar.
- El frontend puede usar estos endpoints para autocompletar etiquetas curriculares al crear/editar items.
- Items creados con `standard_id` / `competency_id` resuelven directamente la entidad sin ambiguedad.

## Criterio de terminado
El frontend del banco de items puede buscar y seleccionar estandares y competencias del catalogo curricular via API, y el backend las resuelve correctamente al guardar el item.
