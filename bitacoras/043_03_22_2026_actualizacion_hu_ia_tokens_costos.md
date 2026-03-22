# Bitacora 043_03_22_2026 10:25:31 actualizacion_hu_ia_tokens_costos

## Que fue lo que se hizo
- Se actualizo la planeacion funcional y tecnica de IA para items en:
  - `planeacion/01_historias_de_usuario/HU_015_EP_002_asistente_ia_generacion_items.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0057_HU_15_EP_002_TODO.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0058_HU_15_EP_002_TODO.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0059_HU_15_EP_002_TODO.md`
- Se consolidaron en backend cambios del modulo `item_ai_assistant` para:
  - forzar correcta en opcion `A` (normalizacion deterministica),
  - exponer `usage` con tokens y costos por peticion,
  - mantener trazabilidad en `metadata`.
- Se extendio frontend en `src/frontend_web/src/components/ItemForm.jsx` para:
  - auto-aplicar borrador IA al formulario (enunciado/opciones/correcta) sin guardado automatico,
  - mostrar tokens de entrada/salida/cached y costos USD por peticion IA.
- Se ajustaron contratos y pruebas asociadas en:
  - `src/backend/app/schemas/item_ai_assistant.py`
  - `src/backend/tests/test_item_ai_assistant_service.py`
  - `src/backend/tests/test_item_ai_assistant_api.py`

## Para que se hizo
- Dejar coherencia entre lo implementado y lo planificado en HU/actividades.
- Mejorar control operativo del modulo IA con visibilidad de consumo/costo para decisiones de uso.
- Asegurar comportamiento consistente para calificacion posterior (correcta siempre en `A` en borradores IA).

## Que problemas se presentaron
- Diferencias entre el comportamiento inicial planificado (aplicar manual) y la expectativa de usuario (ver valores inmediatamente en cuadros de enunciado/opciones).
- Falta de trazabilidad explicita de costos/tokens en la respuesta mostrada al usuario.
- Ajustes de edicion por terminal con sustituciones de texto que requirieron validacion adicional para no romper JSX/strings.

## Como se resolvieron
- Se cambio el flujo de frontend para aplicar automaticamente el borrador generado al formulario, manteniendo guardrail de no guardado automatico.
- Se agrego `usage` estructurado en backend con costos calculados usando tarifas definidas:
  - entrada: 1.25 USD / 1M tokens,
  - cached entrada: 0.125 USD / 1M tokens,
  - salida: 10.00 USD / 1M tokens.
- Se agrego bloque visual `ai-usage` en frontend para mostrar consumo y costo total por solicitud.
- Se ejecutaron validaciones automaticas:
  - `pytest -vv -s tests/test_item_ai_assistant_service.py tests/test_item_ai_assistant_api.py`
  - `npm run build` en `src/frontend_web`.

## Que continua
- Completar pendientes de `ACT_0059`:
  - test de contrato especifico del proveedor OpenAI,
  - E2E generar->aplicar->guardar item,
  - documentacion README backend/frontend de configuracion IA y costos.
- Crear bitacora de cierre cuando `ACT_0059` quede en estado `done`.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
