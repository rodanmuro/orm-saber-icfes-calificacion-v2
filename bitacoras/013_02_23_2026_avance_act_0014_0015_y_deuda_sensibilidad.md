# Bitacora 013_02_23_2026 14:00:06 avance_act_0014_0015_y_deuda_sensibilidad

## Que fue lo que se hizo
- Se implemento backend para `ACT_0014` con endpoint `POST /api/v1/omr/read-photo` que recibe foto via multipart y retorna JSON OMR por pregunta.
- Se creo servicio interno de lectura desde bytes para orquestar alineacion ArUco, clasificacion de burbujas y armado de salida.
- Se implemento frontend para `ACT_0015` en Expo con captura de camara y envio de foto al backend local.
- Se agrego visualizacion de respuesta en app movil (resumen + JSON), junto con estados de carga y errores.
- Se ejecuto prueba real desde celular en LAN con respuesta `200 OK` y lectura efectiva.
- Se ajusto logging backend para depuracion en formato legible por pregunta (`pregunta X: opcion`).

Archivos clave creados/modificados:
- `src/backend/app/api/v1/endpoints/omr_read.py`
- `src/backend/app/api/v1/router.py`
- `src/backend/app/modules/omr_reader/api_service.py`
- `src/backend/app/modules/omr_reader/loader.py`
- `src/backend/tests/test_omr_api_service.py`
- `src/backend/requirements.txt`
- `src/backend/README.md`
- `src/frontend/App.js`
- `src/frontend/src/services/omrRead.js`
- `src/frontend/src/config/api.js`
- `src/frontend/.env.example`
- `src/frontend/README.md`
- `src/frontend/package.json`
- `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0014_HU_08_EP_001_IN_PROGRESS.md`
- `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0015_HU_09_EP_001_IN_PROGRESS.md`

## Para que se hizo
- Completar el flujo MVP movil real: tomar foto en celular, enviarla a backend y obtener lectura de opciones.
- Validar que la arquitectura local por IP LAN funciona para pruebas de campo sin despliegue externo.

## Que problemas se presentaron
- Inicialmente el endpoint retornaba `404` por backend levantado sin los ultimos cambios.
- En capturas con sombra/iluminacion baja, la lectura devolvia muchas preguntas sin marcadas (`-`) aunque la conexion y pipeline estaban operativos.
- El log JSON completo era muy extenso para inspeccion rapida manual.

## Como se resolvieron
- Se reinicio backend con codigo actualizado y se confirmo endpoint operativo con `200 OK`.
- Se validaron fotos con mejor iluminacion y se comprobó lectura correcta en movil.
- Se cambio log de salida a formato linea por pregunta (`pregunta N: opcion`) para depuracion mas rapida.

## Que continua
- Cerrar `ACT_0014` y `ACT_0015` en `DONE` con evidencia de prueba movil exitosa.
- Implementar `ACT_0016` para vista de resultados mas limpia orientada a usuario.
- **Deuda tecnica prioritaria**: robustecer sensibilidad de lectura ante fotos claras/sombra.
  - Lineas propuestas:
    - normalizacion de iluminacion antes de clasificar,
    - umbral adaptativo por zona/burbuja,
    - autoajuste de sensibilidad segun calidad de imagen,
    - reintento automatico con perfil "luz dificil".

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
