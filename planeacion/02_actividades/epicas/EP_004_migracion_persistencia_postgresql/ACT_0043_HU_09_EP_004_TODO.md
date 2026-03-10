estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0043 - Integracion Alembic como mecanismo oficial de migraciones

## Objetivo tecnico
Inicializar Alembic y establecer flujo versionado de esquema como practica obligatoria.

## Tareas implementables
- [ ] Inicializar estructura Alembic en backend.
- [ ] Crear migracion base del esquema vigente.
- [ ] Ajustar pipeline de arranque para aplicar migraciones en lugar de `create_all` operativo.
- [ ] Documentar comando estandar para generar y aplicar nuevas migraciones.

## Evidencias esperadas
- Alembic inicializado y funcionando.
- Migracion base aplicable en PostgreSQL.
- Guia minima para ciclo de migraciones.

## Criterio de terminado
Todo cambio de esquema nuevo se gestiona por Alembic y el esquema vigente puede reconstruirse desde migraciones.
