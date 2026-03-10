# HU_009 - Infra PostgreSQL y migraciones Alembic (EP_004)

## Trazabilidad
- Epica asociada: `EP_004_migracion_persistencia_postgresql.md`
- Dependencias: configuracion actual backend FastAPI + SQLAlchemy.

## Historia de usuario
**Como** equipo tecnico  
**Quiero** disponer de infraestructura PostgreSQL local y migraciones Alembic versionadas  
**Para** evolucionar el esquema de datos de forma controlada y reproducible.

## Criterios de aceptacion
1. Existe una forma documentada de levantar PostgreSQL en desarrollo local.
2. Alembic queda integrado al proyecto y permite aplicar migraciones en orden.
3. El esquema inicial de dominio puede crearse sin usar `create_all` como mecanismo operativo principal.
4. El backend puede arrancar usando `DATABASE_URL` de PostgreSQL.
5. Se documenta el flujo de trabajo para nuevas migraciones de esquema.

## Evidencia esperada
- Configuracion de entorno local PostgreSQL.
- Estructura Alembic inicializada con migracion base del proyecto.
- Instrucciones operativas de migracion y arranque.

## Notas
- Mantener SQLite como soporte local secundario puede evaluarse, pero PostgreSQL se define como destino principal.
