estado: in_progress
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0046 - Validacion de endpoints EP_002 sobre PostgreSQL

## Objetivo tecnico
Ejecutar y ajustar endpoints de banco de items, examenes y versiones en PostgreSQL para asegurar continuidad funcional.

## Tareas implementables
- [x] Validar CRUD de items sobre PostgreSQL.
- [x] Validar creacion de examenes y asociacion de items.
- [x] Validar publicacion de versiones y consistencia de mapeo de opciones.
- [ ] Corregir diferencias SQLite vs PostgreSQL encontradas en API (si aparecen en corrida final local).

## Evidencias esperadas
- Endpoints EP_002 funcionando sobre PostgreSQL.
- Pruebas de integracion backend en verde para rutas criticas.
- Registro de ajustes aplicados.

## Avance actual
- Se agrego prueba de integracion sobre PostgreSQL:
  - `src/backend/tests/test_ep002_postgres_integration.py`
- La prueba cubre E2E de EP_002:
  - creacion/listado de items,
  - creacion de examen,
  - asociacion de items,
  - publicacion de version,
  - consulta de versiones y answer-key.

## Criterio de terminado
Los flujos principales de EP_002 se ejecutan de extremo a extremo en PostgreSQL.
