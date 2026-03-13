estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0056 - Script de arranque PostgreSQL y migracion SQLite a PostgreSQL

## Objetivo tecnico
Proveer herramientas operativas para: (a) arrancar el backend apuntando a PostgreSQL de forma reproducible y (b) migrar items existentes en SQLite hacia PostgreSQL sin duplicados.

## Tareas implementables
- [x] Crear `src/backend/run-app-postgres.sh`:
  - Valida existencia del entorno virtual antes de arrancar.
  - Exporta `DATABASE_URL` apuntando a PostgreSQL local por defecto.
  - Soporta modo `--reload` controlable via variable de entorno `RELOAD`.
  - Ejecuta `uvicorn app.main:app` con host/port configurables.
- [x] Crear `src/backend/scripts/migrate_sqlite_items_to_postgres.py`:
  - Lee docentes, estandares, competencias e items desde SQLite.
  - Los inserta en PostgreSQL mapeando IDs y evitando duplicados mediante firma de item (hash de campos clave).
  - Imprime reporte de ejecucion: creados / omitidos por categoria.
  - Es idempotente: puede ejecutarse multiples veces sin crear duplicados.

## Archivos creados
- `src/backend/run-app-postgres.sh` (nuevo)
- `src/backend/scripts/migrate_sqlite_items_to_postgres.py` (nuevo)

## Evidencias esperadas
- `bash src/backend/run-app-postgres.sh` levanta el backend conectado a PostgreSQL sin errores.
- Ejecutar el script de migracion transfiere items de SQLite a PostgreSQL y omite los ya existentes en corridas posteriores.

## Criterio de terminado
El equipo puede arrancar el backend en PostgreSQL con un solo comando y migrar datos previos de SQLite sin intervencion manual sobre las tablas.
