# EP_004 - Migracion de persistencia a PostgreSQL

## Objetivo tecnico
Migrar la persistencia principal del backend desde SQLite a PostgreSQL, estandarizando migraciones versionadas y garantizando compatibilidad funcional de los modulos EP_002 y EP_003.

## Alcance
- Definir entorno base PostgreSQL para desarrollo local y ejecucion de backend.
- Incorporar migraciones versionadas (Alembic) como mecanismo oficial de evolucion de esquema.
- Portar el esquema actual de dominio (items, examenes, versiones, intentos OMR y catalogos curriculares).
- Habilitar estrategia de migracion de datos iniciales desde SQLite (cuando aplique).
- Validar endpoints y pruebas criticas sobre PostgreSQL.
- Mantener desacople para conservar posibilidad de uso de SQLite en escenarios locales de soporte puntual.

## Fuera de alcance
- Migracion de historico completo productivo con ventana cero downtime.
- Ajustes de performance avanzada (particionado, tuning profundo).
- Replicacion, alta disponibilidad y operacion multi-nodo.
- Migracion a otros motores (MariaDB/MySQL) en este incremento.

## Entregables verificables
- Configuracion backend funcional con `DATABASE_URL` apuntando a PostgreSQL.
- Base Alembic inicializada y migraciones aplicables para el esquema actual.
- Script/procedimiento reproducible para bootstrap de datos semilla.
- Evidencia de pruebas backend clave ejecutando sobre PostgreSQL.
- Documentacion operativa para levantar entorno y ejecutar migraciones.

## Restricciones tecnicas
- SQLAlchemy se mantiene como capa de acceso principal.
- Se evita SQL crudo acoplado al motor salvo casos justificados.
- Toda evolucion de esquema nueva debe entrar por Alembic.
- Se preserva compatibilidad funcional de APIs ya consumidas por frontend web y movil.

## Criterios de aceptacion
1. El backend levanta y opera contra PostgreSQL en entorno local con configuracion documentada.
2. El esquema completo vigente se crea via Alembic sin depender de `create_all` como mecanismo principal.
3. Los flujos criticos de EP_002 y EP_003 pasan pruebas sobre PostgreSQL.
4. Existe ruta clara de migracion de datos base desde SQLite para desarrollo.
5. El equipo puede continuar nuevas funcionalidades sobre PostgreSQL sin bloquear el roadmap funcional.
