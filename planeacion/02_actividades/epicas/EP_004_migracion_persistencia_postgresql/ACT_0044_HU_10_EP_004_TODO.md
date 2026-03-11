estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0044 - Portabilidad de esquema de dominio a PostgreSQL

## Objetivo tecnico
Validar y ajustar tipos, constraints y relaciones del esquema actual para compatibilidad completa con PostgreSQL.

## Tareas implementables
- [x] Revisar entidades y constraints del dominio actual en motor PostgreSQL.
- [x] Ajustar tipos de columna (JSON, fechas, booleanos, textos) segun comportamiento esperado.
- [x] Validar indices y unicidad de claves de negocio (`teacher_id + exam_code`, etc.).
- [x] Confirmar integridad referencial en flujos de insercion/actualizacion.

## Evidencias esperadas
- Esquema completo creado sin errores en PostgreSQL.
- Relaciones y constraints funcionando segun reglas de negocio.
- Registro de ajustes de compatibilidad aplicados.

## Avance actual
- Migracion base PostgreSQL publicada en `src/backend/alembic/versions/20260310_0001_initial_schema.py`.
- Se agrego script de validacion estructural en `src/backend/scripts/validate_postgres_schema.py` para:
  - tablas esperadas,
  - unique constraints criticos,
  - foreign keys basicas,
  - consultas minimas de integridad.
- Validacion final ejecutada en entorno local PostgreSQL:
  - salida: `[schema-check] OK - esquema y constraints basicos validados`.

## Criterio de terminado
El modelo de datos actual queda estable y consistente en PostgreSQL.
