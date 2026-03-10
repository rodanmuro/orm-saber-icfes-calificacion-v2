estado: todo
prioridad: media
sprint: S4
owner: por_definir

# ACT_0045 - Seed y carga de datos base para desarrollo

## Objetivo tecnico
Establecer proceso reproducible de carga de datos base/dummy sobre PostgreSQL para continuidad de pruebas funcionales.

## Tareas implementables
- [ ] Adaptar scripts de seed existentes al entorno PostgreSQL.
- [ ] Definir dataset minimo de validacion (docente, items, examen, version).
- [ ] Ejecutar carga limpia y verificar consistencia de relaciones.
- [ ] Documentar procedimiento de reinicio + reseed.

## Evidencias esperadas
- Datos semilla disponibles en PostgreSQL.
- Flujo de reseed repetible sin inconsistencias.
- Validacion de claves correctas en examen/version.

## Criterio de terminado
El entorno PostgreSQL puede poblarse con datos funcionales de prueba en forma automatizable.
