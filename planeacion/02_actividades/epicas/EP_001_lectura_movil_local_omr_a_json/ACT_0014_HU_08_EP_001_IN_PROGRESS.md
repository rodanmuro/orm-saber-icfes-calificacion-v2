estado: in_progress
prioridad: alta
sprint: S2
owner: codex

# ACT_0014 - Endpoint backend para recepcion de foto y lectura OMR

## Objetivo tecnico
Exponer en FastAPI un endpoint que reciba foto desde movil y retorne JSON de lectura por pregunta.

## Tareas implementables
- [x] Definir contrato de request/response para carga de imagen y referencia de template.
- [x] Implementar endpoint multipart para recibir archivo de foto.
- [x] Orquestar pipeline actual (carga, alineacion, clasificacion, armado de JSON) dentro del endpoint.
- [x] Retornar errores controlados con mensajes legibles para casos invalidos.
- [ ] Ejecutar validacion LAN con backend corriendo y llamada HTTP desde cliente movil.

## Evidencias esperadas
- Endpoint implementado en `src/backend`:
  - `src/backend/app/api/v1/endpoints/omr_read.py`
  - `src/backend/app/api/v1/router.py`
- Servicio backend de procesamiento de foto por bytes:
  - `src/backend/app/modules/omr_reader/api_service.py`
- Ajuste de dependencias multipart:
  - `src/backend/requirements.txt`
- Pruebas unitarias del servicio:
  - `src/backend/tests/test_omr_api_service.py`
- Ejecucion local validada sobre imagen real via servicio:
  - lectura `foto_001.jpeg` -> `quality_summary` y opciones por pregunta correctas.

## Criterio de terminado
Desde cliente externo se puede enviar una foto al backend y recibir respuesta OMR estructurada o error claro.
