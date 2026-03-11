estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0043 - Integracion Alembic como mecanismo oficial de migraciones

## Objetivo tecnico
Inicializar Alembic y establecer flujo versionado de esquema como practica obligatoria.

## Tareas implementables
- [x] Inicializar estructura Alembic en backend.
- [x] Crear migracion base del esquema vigente.
- [x] Ajustar pipeline de arranque para aplicar migraciones en lugar de `create_all` operativo.
- [x] Documentar comando estandar para generar y aplicar nuevas migraciones.
- [x] Validar ejecucion `alembic upgrade head` sobre PostgreSQL local en entorno del usuario.

## Evidencias esperadas
- Alembic inicializado y funcionando.
- Migracion base aplicable en PostgreSQL.
- Guia minima para ciclo de migraciones.

## Avance actual
- Estructura Alembic creada en `src/backend/alembic` con `env.py` y template `script.py.mako`.
- Configuracion creada en `src/backend/alembic.ini`.
- Migracion base creada: `src/backend/alembic/versions/20260310_0001_initial_schema.py`.
- `src/backend/app/db/init_db.py` actualizado para ejecutar migraciones (`upgrade head`) en arranque.
- Documentacion de comandos Alembic agregada en `src/backend/README.md`.
- Evidencia local validada:
  - `alembic upgrade head` ejecutado sobre PostgreSQL.
  - Migracion aplicada: `20260310_0001_initial_schema`.
  - Seed dummy ejecutado con exito sobre PostgreSQL (`exam_code=1234`, 40 preguntas).

## Criterio de terminado
Todo cambio de esquema nuevo se gestiona por Alembic y el esquema vigente puede reconstruirse desde migraciones.
