# Bitacora 045_03_23_2026 08:50:43 estabilidad_ia_json_editor

## Que fue lo que se hizo
- Se estabilizo el flujo de generacion de items con IA para reducir errores `HTTP 502` por salida no parseable.
- Se reforzo el proveedor OpenAI en `src/backend/app/modules/item_ai_assistant/providers/openai_provider.py`:
  - llamada a Responses con formato JSON forzado (`json_object`),
  - parser robusto para extraer el primer objeto JSON valido cuando viene ruido alrededor,
  - mensajes de error mas informativos en fallas no reintentables.
- Se mejoro la validacion de `media_spec` en `src/backend/app/modules/item_ai_assistant/validators.py`:
  - compatibilidad con `spec.data=[{label,value}]`,
  - compatibilidad para grafico `pie` cuando llega `values` en lugar de `sizes`,
  - normalizacion interna a contrato esperado (`labels` + `sizes` para pie).
- Se mantuvo y amplió cobertura automatica:
  - `src/backend/tests/test_item_ai_assistant_service.py` (nuevos casos de normalizacion y recuperacion),
  - `src/backend/tests/test_item_ai_openai_provider_retry.py` (ajuste de firma mock por nuevos argumentos),
  - `src/backend/tests/test_item_ai_assistant_api.py`.
- Se ejecuto validacion e2e real contra proveedor OpenAI desde backend con 5 intentos consecutivos (prompt de porcentajes + grafica circular).
- En frontend se dejo avance UX solicitado:
  - `src/frontend_web/src/components/ItemForm.jsx` (bloque Curricular reubicado antes de Instruccion IA),
  - `src/frontend_web/src/editor/ResizableImage.js` (resize por cuatro esquinas),
  - `src/frontend_web/src/styles.css` (estados visuales de seleccion y handles).

## Para que se hizo
- Reducir friccion operativa del docente al crear preguntas con IA.
- Evitar el escenario de "intentar varias veces" por errores de parsing del modelo.
- Hacer el flujo mas tolerante a variaciones reales del proveedor (JSON con formas alternativas en `media_spec`).
- Mejorar usabilidad del editor para trabajo con imagenes y orden de captura curricular.

## Que problemas se presentaron
- Problema no tecnico (impacto de usuario): el docente recibia muchos `HTTP 502` y debia reintentar varias veces para obtener un borrador.
- Problema tecnico principal:
  - respuestas del modelo no siempre llegaban como JSON limpio,
  - cuando llegaban parseables, el campo `media_spec` podia venir en formas no previstas por el validador (por ejemplo `data` o `values` para pie).
- Durante el ajuste, una version intermedia de schema estricto devolvio error de proveedor (`invalid_json_schema`), bloqueando toda la solicitud.

## Como se resolvieron
- Se cambio la estrategia a formato JSON forzado (`json_object`) + validacion backend robusta, en lugar de schema estricto en la llamada.
- Se implemento parseo defensivo en proveedor:
  - intento directo de `json.loads`,
  - fallback para extraer el primer objeto JSON completo si hay texto adicional.
- Se agrego normalizacion de contrato en `validators.py`:
  - `spec.data` -> `labels` + `values/sizes`,
  - para `pie`, si no hay `sizes` pero si `values`, se convierte automaticamente.
- Se verifico por capas:
  - tests automatizados backend (servicio/api/proveedor),
  - prueba e2e real 5/5 exitosa en el escenario de porcentajes con grafica circular.

## Que continua
- Ejecutar validacion manual en frontend con prompts de docente reales y registrar tasa de exito en bitacora siguiente.
- Ajustar prompts para reducir necesidad de reparacion (`ai_repaired`) sin sacrificar robustez.
- Si reaparecen errores no reintentables, registrar `detail` exacto y clasificar por causa (auth, cuota, formato, timeout).

*(Referencias clave: `src/backend/app/modules/item_ai_assistant/providers/openai_provider.py`, `src/backend/app/modules/item_ai_assistant/validators.py`, `src/backend/tests/test_item_ai_assistant_service.py`, `src/backend/tests/test_item_ai_openai_provider_retry.py`, `src/frontend_web/src/editor/ResizableImage.js`.)*
