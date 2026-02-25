estado: done
prioridad: alta
sprint: S2
owner: codex

# ACT_0014 - Endpoint backend para recepcion de foto y lectura OMR

## Objetivo tecnico
Exponer endpoint FastAPI multipart para recibir foto y devolver lectura OMR estructurada.

## Tareas implementables
- [x] Definir contrato de request/response para carga de imagen y template.
- [x] Implementar endpoint multipart de recepcion de foto.
- [x] Orquestar pipeline backend de lectura por bytes.
- [x] Retornar errores controlados y legibles.
- [x] Validar llamada HTTP desde cliente movil en LAN.

## Evidencias esperadas
- Endpoint y enrutamiento:
  - `src/backend/app/api/v1/endpoints/omr_read.py`
  - `src/backend/app/api/v1/router.py`
- Servicio de lectura:
  - `src/backend/app/modules/omr_reader/api_service.py`
- Dependencias/pruebas:
  - `src/backend/requirements.txt`
  - `src/backend/tests/test_omr_api_service.py`

## Cierre breve
El backend recibe fotos desde movil y responde JSON OMR en entorno LAN, incluyendo trazabilidad de imagen/resultado.

## Criterio de terminado
Desde cliente externo se envia foto al backend y se recibe respuesta OMR estructurada o error claro.
