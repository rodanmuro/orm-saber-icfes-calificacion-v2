estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0046 - Validacion de endpoints EP_002 sobre PostgreSQL

## Objetivo tecnico
Ejecutar y ajustar endpoints de banco de items, examenes y versiones en PostgreSQL para asegurar continuidad funcional.

## Tareas implementables
- [ ] Validar CRUD de items sobre PostgreSQL.
- [ ] Validar creacion de examenes y asociacion de items.
- [ ] Validar publicacion de versiones y consistencia de mapeo de opciones.
- [ ] Corregir diferencias SQLite vs PostgreSQL encontradas en API.

## Evidencias esperadas
- Endpoints EP_002 funcionando sobre PostgreSQL.
- Pruebas de integracion backend en verde para rutas criticas.
- Registro de ajustes aplicados.

## Criterio de terminado
Los flujos principales de EP_002 se ejecutan de extremo a extremo en PostgreSQL.
