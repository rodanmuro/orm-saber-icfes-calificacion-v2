# Bitacora 066_04_28_2026 14:52:29 portal_resultados_5174

## Que fue lo que se hizo
- Se implemento un nuevo modulo backend para portal de estudiantes en `src/backend/app/api/v1/endpoints/student_portal.py`.
- Se registraron nuevas rutas en `src/backend/app/api/v1/router.py` bajo el prefijo `student-portal`.
- Se agregaron endpoints para:
  - Autenticacion simple por correo + documento.
  - Listado de intentos calificados del estudiante autenticado.
  - Exportacion de PDF individual por intento, incluyendo overlay y resumen de respuestas.
- Se construyo un frontend separado para estudiantes en `src/frontend_results` (Vite + React) con puerto 5174:
  - Login de consulta individual.
  - Tabla de resultados por intento.
  - Descarga de PDF por intento.
- Se ajusto CORS para soportar origenes `5174` en:
  - `src/backend/app/core/config.py`
  - `src/backend/.env.example`
- Se agrego configuracion en `.env` local para incluir `CORS_ALLOWED_ORIGINS` con `5173` y `5174`.

## Para que se hizo
- Separar el acceso de estudiantes del dashboard docente para evitar ingreso accidental a la raiz de administracion.
- Habilitar una forma operativa en clase para consulta y descarga de resultados individuales por LAN.
- Entregar evidencia visual de calificacion mediante overlay junto con resumen textual en PDF.

## Que problemas se presentaron
- El portal en `5174` presento error de red por preflight CORS (`OPTIONS ... 400 Bad Request`).
- La causa fue que el backend solo permitia origenes `5173` y no aceptaba `5174`.

## Como se resolvieron
- Se extendio la lista de origenes CORS permitidos para incluir:
  - `http://localhost:5174`
  - `http://127.0.0.1:5174`
- Se aplico el cambio tanto en defaults de codigo como en archivos de ejemplo de entorno.
- Se dejo indicado reiniciar backend para recargar configuracion y permitir preflight correcto.

## Que continua
- Probar end-to-end con estudiantes reales:
  - autenticacion,
  - listado de intentos,
  - descarga de PDF con overlay.
- Agregar hardening minimo al portal de estudiantes:
  - rate limit de login,
  - expiracion corta de sesion,
  - mensajes de error controlados.
- Evaluar paso posterior de integrar este modulo al frontend principal cuando exista autenticacion docente/estudiante formal.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
