# Bitacora 047_03_25_2026 09:55:14 fase2_media_specs_multigraficos

## Que fue lo que se hizo
- Se implemento la fase 2 del asistente IA para soportar multiples graficas por item usando `media_specs` (lista) y no solo `media_spec` (objeto unico).
- Se mantuvo compatibilidad hacia atras: el backend sigue aceptando/respondiendo `media_spec` mientras habilita `media_specs`.
- Se reforzaron guardrails de validacion para medios graficos:
  - maximo 5 graficas por item,
  - targets unicos (sin duplicados),
  - validacion estructural por cada grafica.
- Se mejoro el render de barras para mostrar el valor numerico sobre cada barra, evitando inferencia visual "a ojo".
- Se actualizo prompt version y contrato de salida para que el modelo devuelva `media_specs` y evite repetir en el enunciado los mismos valores exactos mostrados en la grafica.
- Se ajusto frontend de `Editar item` para:
  - iterar y renderizar todas las entradas de `media_specs`,
  - insertar cada grafica en su target correspondiente (`statement` u opcion),
  - conservar fallback de compatibilidad con `media_spec`.
- Archivos modificados:
  - `src/backend/app/modules/item_ai_assistant/validators.py`
  - `src/backend/app/modules/item_ai_assistant/prompt_builder.py`
  - `src/backend/app/modules/item_ai_assistant/media_service.py`
  - `src/backend/app/modules/item_ai_assistant/service.py`
  - `src/backend/app/modules/item_ai_assistant/domain.py`
  - `src/backend/app/schemas/item_ai_assistant.py`
  - `src/backend/app/api/v1/endpoints/ai_assistant.py`
  - `src/backend/tests/test_item_ai_assistant_service.py`
  - `src/backend/tests/test_item_ai_assistant_api.py`
  - `src/backend/tests/test_item_ai_media_api.py`
  - `src/frontend_web/src/components/ItemForm.jsx`

## Para que se hizo
- Para permitir ejercicios mas ricos donde el enunciado y/o opciones puedan incluir una o varias graficas sin hacks manuales.
- Para robustecer el flujo IA frente a casos reales de evaluacion (preguntas con evidencia visual en mas de un bloque).
- Para mejorar consistencia pedagogica: los datos se leen desde la grafica y no desde texto duplicado.

## Que problemas se presentaron
- El contrato inicial del modulo estaba disenado para una sola grafica (`media_spec`), lo que limitaba la escalabilidad del flujo.
- Habia riesgo de romper compatibilidad con pruebas y frontend existente si se eliminaba el campo antiguo.
- En la operacion de edicion por consola se tuvo cuidado con potenciales inconsistencias de quoting al reescribir bloques grandes.

## Como se resolvieron
- Se introdujo un contrato dual temporal (`media_spec` + `media_specs`) para migrar sin romper consumidores existentes.
- Se centralizo la validacion de lista de graficas en backend con reglas de unicidad y limite maximo.
- Se adapto frontend para procesar lista de graficas y aplicar inserciones por target en un solo flujo.
- Se extendio cobertura de pruebas para:
  - media_specs validos con targets distintos,
  - rechazo por targets duplicados,
  - media API con valores numericos string,
  - regresion general del asistente.
- Validaciones ejecutadas:
  - `pytest -q tests/test_item_ai_assistant_service.py tests/test_item_ai_assistant_api.py tests/test_item_ai_media_api.py` -> 17 passed.
  - `npm run build` en `src/frontend_web` -> build exitoso.

## Que continua
- Probar manualmente en UI casos con 3-5 graficas en distintos targets para validar UX de lectura y guardado.
- Evaluar si en siguiente iteracion se depreca formalmente `media_spec` para dejar solo `media_specs`.
- Documentar en README del backend/frontend el nuevo contrato multi-grafico con ejemplos de payload.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
