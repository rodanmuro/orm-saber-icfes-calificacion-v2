# Bitacora 036_03_11_2026 17:03:37 cierre_act_0043_0044_0045_migracion_postgresql

## Que fue lo que se hizo
- Se completo la base tecnica de migracion de persistencia a PostgreSQL en tres actividades encadenadas:
  - ACT_0043 (integracion Alembic y migracion base),
  - ACT_0044 (validacion de esquema/constraints en PostgreSQL),
  - ACT_0045 (reseed y verificacion reproducible de dataset dummy).
- Cambios principales de implementacion:
  - Se integro Alembic en backend con configuracion y migracion inicial (`20260310_0001_initial_schema`).
  - Se cambio el flujo de inicializacion DB para ejecutar migraciones (`upgrade head`) en lugar de `create_all` operativo.
  - Se agregaron scripts de soporte para operacion y validacion:
    - `check_database_connection.py`
    - `validate_postgres_schema.py`
    - `reseed_dummy_dataset.py`
    - `verify_dummy_dataset.py`
  - Se actualizo README backend con comandos de onboarding, migraciones y validaciones sobre PostgreSQL.
- Evidencia funcional registrada en entorno local:
  - Migracion aplicada y esquema activo en PostgreSQL.
  - Dataset dummy operativo con:
    - 1 docente,
    - 1 examen (`exam_code=1234`),
    - 40 preguntas,
    - 1 version (`V001`) y 40 registros de mapeo en `exam_version_item`.

## Para que se hizo
- Para que el proyecto deje de depender de SQLite como ruta principal y tenga una base de datos mas preparada para crecimiento.
- Para que cualquier desarrollador nuevo pueda levantar backend + base de datos con una ruta clara y repetible.
- Para garantizar que el entorno de desarrollo tenga datos de prueba listos para validar APIs y flujo OMR sin configuraciones manuales ambiguas.

## Que problemas se presentaron
- Se presento conflicto de nombres entre el paquete `alembic` y la carpeta local `alembic/` al intentar importar `from alembic import command`.
- El entorno virtual local no tenia inicialmente todas las dependencias instaladas (faltaba `alembic`), lo que genero errores de ejecucion.
- Hubo ejecuciones con `DATABASE_URL` por defecto a SQLite cuando la validacion debia hacerse contra PostgreSQL.

## Como se resolvieron
- Se reemplazo la llamada programatica de Alembic por ejecucion robusta via `python -m alembic` usando el mismo interprete del entorno activo.
- Se actualizo `requirements.txt` para incluir dependencias de PostgreSQL y migraciones.
- Se documento y estandarizo el uso explicito de `DATABASE_URL` para evitar validar contra el motor equivocado.
- Se agregaron scripts de comprobacion para convertir cada paso en evidencia objetiva (`db-check`, `schema-check`, `dummy-check`).

## Explicacion de alto nivel (onboarding)
Para una persona nueva en el proyecto, el flujo ahora se entiende asi:

1. **Conectar la base de datos**:
   - El proyecto usa PostgreSQL como motor principal.
   - Se configura `DATABASE_URL` y se valida conexion con un comando simple.

2. **Crear estructura automaticamente**:
   - Al iniciar backend o ejecutar migraciones, el sistema aplica la version actual de la estructura de tablas.
   - Esto evita crear tablas manualmente.

3. **Cargar datos de ejemplo listos para pruebas**:
   - Con un comando de reseed se crea un examen dummy completo (docente, preguntas, examen y version).
   - Con otro comando se valida que quedo consistente.

4. **Resultado practico**:
   - Cualquier desarrollador puede clonar el repo, instalar dependencias, levantar PostgreSQL y tener entorno funcional en poco tiempo.

## Que continua
- Iniciar ACT_0046 para validar endpoints de EP_002 sobre PostgreSQL (items, examenes, versiones).
- Ejecutar bateria minima de pruebas API con base PostgreSQL ya poblada por reseed.
- Mantener alineado README + actividades conforme avance la migracion funcional completa.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
