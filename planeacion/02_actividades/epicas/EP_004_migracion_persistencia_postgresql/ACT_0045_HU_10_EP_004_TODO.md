estado: done
prioridad: media
sprint: S4
owner: por_definir

# ACT_0045 - Seed y carga de datos base para desarrollo

## Objetivo tecnico
Establecer proceso reproducible de carga de datos base/dummy sobre PostgreSQL para continuidad de pruebas funcionales.

## Tareas implementables
- [x] Adaptar scripts de seed existentes al entorno PostgreSQL.
- [x] Definir dataset minimo de validacion (docente, items, examen, version).
- [x] Ejecutar carga limpia y verificar consistencia de relaciones.
- [x] Documentar procedimiento de reinicio + reseed.

## Evidencias esperadas
- Datos semilla disponibles en PostgreSQL.
- Flujo de reseed repetible sin inconsistencias.
- Validacion de claves correctas en examen/version.

## Avance actual
- Se agrego script de reseed oficial: `src/backend/scripts/reseed_dummy_dataset.py`.
- Se agrego script de verificacion de dataset: `src/backend/scripts/verify_dummy_dataset.py`.
- README actualizado con comandos de reseed + verificacion sobre PostgreSQL.
- Dataset definido:
  - docente dummy: `docente.dummy40@omr.local`
  - examen: `exam_code=1234`
  - 40 preguntas base
  - version publicada: `V001` con barajado reproducible.
- Validacion final ejecutada en entorno local:
  - salida de verificacion: `[dummy-check] OK - dataset dummy validado`
  - consistencia: `teacher=1 exam=1 exam_item=40 version=1 version_item=40`.

## Criterio de terminado
El entorno PostgreSQL puede poblarse con datos funcionales de prueba en forma automatizable.
