# Bitacora 019_02_24_2026 06:56:10 avance_act_0022_interfaz_y_validacion_e2e

## Que fue lo que se hizo
- Se inicio la implementacion de `ACT_0022` para desacoplar el lector OMR por estrategia de motor.
- Se creo el modulo de estrategia/contrato:
  - `src/backend/app/modules/omr_reader/reader_strategy.py`
- Se actualizaron errores de dominio para backend no soportado o no listo:
  - `src/backend/app/modules/omr_reader/errors.py`
- Se agrego configuracion de backend lector por entorno (default `classic`):
  - `src/backend/app/core/config.py`
- Se refactorizo el servicio principal de lectura para resolver motor por configuracion y ejecutar el engine:
  - `src/backend/app/modules/omr_reader/api_service.py`
- Se ajustaron pruebas del servicio OMR para cubrir selector/diagnostico de backend:
  - `src/backend/tests/test_omr_api_service.py`
- Se actualizo estado Scrum de actividad:
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0022_HU_13_EP_001_IN_PROGRESS.md`
- Se ejecuto validacion automatica y manual:
  - tests OMR backend en `.venv`.
  - prueba E2E con frontend Expo Go + backend en nueva LAN.

## Para que se hizo
- Introducir una interfaz comun para soportar dos motores (`classic` y `gemini`) sin romper el endpoint actual ni el esquema JSON que consume frontend.
- Dejar listo el punto de extension para `ACT_0023` (integracion real de Gemini).

## Que problemas se presentaron
- En entorno sin `.venv` activo, los tests no corrien por falta de `cv2`.
- Al cambiar de red LAN fue necesario actualizar la URL del backend en frontend (`EXPO_PUBLIC_API_BASE_URL`).

## Como se resolvieron
- Se activaron pruebas con el entorno virtual del proyecto (`.venv`) y se confirmo que no hay regresion del bloque OMR:
  - `pytest -q src/backend/tests/test_omr_api_service.py` -> 5 passed
  - `pytest -q src/backend/tests/test_omr_*.py` -> 17 passed
- Se ejecuto test de integracion con imagen real en `mobile_uploads`:
  - `mobile_20260223_153237_e2b2c4cf.jpg`
  - resultado: test passed con metricas esperadas para la captura.
- Se actualizo `.env` del frontend a la nueva IP LAN para revalidar flujo E2E desde celular.

## Que continua
- Cerrar `ACT_0022` con evidencia final de no regresion (salida `classic` estable bajo interfaz).
- Iniciar `ACT_0023` para implementar `GeminiOMRReadEngine` con parseo estructurado y manejo de errores controlado.
- Mantener `ACT_0017` a `ACT_0021` en `BLOCKED` hasta terminar el primer ciclo comparativo `classic vs gemini`.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
