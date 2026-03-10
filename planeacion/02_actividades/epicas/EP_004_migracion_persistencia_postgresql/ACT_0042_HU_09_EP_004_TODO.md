estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0042 - Provisionamiento PostgreSQL local para backend

## Objetivo tecnico
Habilitar entorno PostgreSQL local reproducible para ejecutar backend y pruebas de desarrollo.

## Tareas implementables
- [x] Definir mecanismo de provisionamiento local por servicio del sistema (sin Docker).
- [x] Configurar variables de entorno para `DATABASE_URL` PostgreSQL.
- [x] Verificar conectividad backend -> PostgreSQL en ejecucion final local.
- [x] Documentar arranque/parada del entorno en README tecnico.

## Evidencias esperadas
- PostgreSQL local operativo y accesible desde backend.
- Backend iniciando con `DATABASE_URL` PostgreSQL.
- Instrucciones de uso local publicadas.

## Avance actual
- Se actualizo `src/backend/.env.example` con `DATABASE_URL` PostgreSQL (`postgresql+psycopg`).
- Se agrego `psycopg[binary]` en `src/backend/requirements.txt`.
- Se agrego script de verificacion de conexion en `src/backend/scripts/check_database_connection.py`.
- Se documento flujo operativo sin Docker en `src/backend/README.md` (start/stop, creacion de rol/db, check de conexion).
- Verificacion final ejecutada en entorno local del usuario:
  - `DATABASE_URL=postgresql+psycopg://administrador:12345678@localhost:5432/omr_app`
  - Resultado: `[db-check] OK - SELECT 1 => 1`.

## Criterio de terminado
El equipo puede levantar PostgreSQL local y conectar el backend sin pasos manuales ambiguos.
