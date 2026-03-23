# Bitacora 044_03_22_2026 21:08:19 e2e_media_spec_autoreparacion_ia

## Que fue lo que se hizo
- Se completo el flujo end-to-end para generar preguntas con grafico desde el Asistente IA en frontend:
  - `src/backend/app/modules/item_ai_assistant/prompt_builder.py`
  - `src/backend/app/modules/item_ai_assistant/service.py`
  - `src/backend/app/modules/item_ai_assistant/validators.py`
  - `src/backend/app/modules/item_ai_assistant/domain.py`
  - `src/backend/app/schemas/item_ai_assistant.py`
  - `src/backend/app/api/v1/endpoints/ai_assistant.py`
  - `src/backend/app/modules/item_ai_assistant/media_service.py` (nuevo)
  - `src/backend/tests/test_item_ai_assistant_service.py`
  - `src/backend/tests/test_item_ai_assistant_api.py`
  - `src/backend/tests/test_item_ai_media_api.py` (nuevo)
  - `src/backend/requirements.txt`
  - `src/frontend_web/src/api/itemsApi.js`
  - `src/frontend_web/src/api/assetsApi.js`
  - `src/frontend_web/src/components/ItemForm.jsx`
- Se agrego soporte de `media_spec` opcional en la respuesta de `POST /api/v1/ai/generate-item`.
- Se agrego endpoint `POST /api/v1/ai/generate-media` para render deterministico de graficos (`bar`, `pie`) y guardado en assets.
- Se implemento auto-aplicacion en frontend: si el borrador IA trae `media_spec`, el frontend llama `generate-media` e inserta la imagen en el destino (`statement` o `option_*`).
- Se endurecio validacion/normalizacion de `media_spec` para aceptar entradas mas naturales (listas en texto, conversion numerica, labels autogenerados cuando faltan).
- Se implemento autoreparacion en backend: si la primera salida IA no valida contrato, se hace segundo intento con prompt de correccion interno.
- Se ejecutaron pruebas:
  - `pytest -vv -s tests/test_item_ai_assistant_service.py tests/test_item_ai_assistant_api.py tests/test_item_ai_media_api.py` (8 passed)
  - `npm run build` en `src/frontend_web` (ok)

## Para que se hizo
- Permitir que el docente solicite preguntas con graficos usando lenguaje natural, sin conocer JSON ni estructura interna.
- Reducir errores 422 recurrentes por salida parcialmente malformada del modelo IA.
- Dejar un flujo robusto y demostrable en frontend para generar, visualizar e insertar graficos en el item antes de guardar.

## Que problemas se presentaron
- El entorno de herramientas del agente fallo por sandbox (`bwrap: Unknown option --argv0`), bloqueando comandos normales.
- Se presentaron errores 422 en `media_spec` (especialmente `labels`/`sizes` en `pie`) por variabilidad de salida del modelo.
- En frontend, las rutas relativas de imagen requerian normalizacion para verse correctamente desde el origen del cliente web.
- Una prueba inicial de autoreparacion no disparaba segundo intento porque el caso de entrada era normalizable y ya no fallaba validacion.

## Como se resolvieron
- Se ejecuto trabajo fuera de sandbox mediante comandos escalados para poder continuar implementacion y validacion.
- Se reforzo `validators.py` con coercion y normalizacion:
  - `labels` desde lista o texto.
  - `values/sizes` desde lista o texto a numeros.
  - labels por defecto cuando faltan y hay datos validos.
- Se agrego logica de autoreparacion en `service.py`:
  - Primer intento normal.
  - Si falla validacion, segundo intento con mensaje de reparacion.
  - Consolidacion de tokens/costos de ambos intentos.
  - Bandera `ai_repaired` en metadata.
- Se conecto frontend (`ItemForm.jsx`) para auto-insertar el `insert_doc` retornado por `generate-media` en el campo objetivo.
- Se actualizo prueba de autoreparacion para forzar fallo no normalizable en el primer intento y confirmar segundo intento.

## Que continua
- Ajustar prompt y guardrails para mejorar cobertura de `pie` cuando el usuario pide porcentajes en lenguaje libre.
- Ampliar tipos de grafico en `chart_deterministic` (por ejemplo `line`, `scatter`) siguiendo el mismo contrato `media_spec`.
- Evaluar registro de telemetria de fallos de formato IA para iterar prompt de manera continua.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
