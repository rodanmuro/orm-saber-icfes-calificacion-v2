# Bitacora 052_03_26_2026 21:49:05 modelos_duales_openai_groq_dificultades

## Que fue lo que se hizo
- Se implemento soporte dual de proveedores IA para el modulo de generacion de items (`openai` y `groq`) en backend.
- Se agrego seleccion de proveedor/modelo en frontend (panel "Asistente IA (borrador)") para elegir dinamicamente el modelo por solicitud.
- Se creo el proveedor Groq dedicado y se integro en el flujo principal del servicio:
  - `src/backend/app/modules/item_ai_assistant/providers/groq_provider.py`
  - `src/backend/app/modules/item_ai_assistant/service.py`
  - `src/backend/app/modules/item_ai_assistant/domain.py`
- Se extendio el contrato API para recibir `ai_provider` y `ai_model`:
  - `src/backend/app/schemas/item_ai_assistant.py`
  - `src/backend/app/api/v1/endpoints/ai_assistant.py`
- Se actualizo configuracion para ambos proveedores:
  - `src/backend/app/core/config.py`
  - `src/backend/.env.example`
  - `src/backend/.env.template`
- Se agrego dependencia Groq en backend:
  - `src/backend/requirements.txt`
- Se robustecio el procesamiento del output para tolerar diferencias de formato entre modelos:
  - normalizacion de estructuras Tiptap con strings sueltos en `statement_doc/options_doc`.
  - normalizacion de tablas con columnas fantasma.
  - archivos: `src/backend/app/modules/item_ai_assistant/validators.py`, `src/backend/app/modules/item_ai_assistant/service.py`.
- Se ajusto UI para no ocupar ancho completo en el select de modelo:
  - `src/frontend_web/src/components/ItemForm.jsx`
  - `src/frontend_web/src/styles.css`
- Se ejecutaron pruebas y verificaciones relevantes:
  - `pytest` del modulo IA (service/api) en verde en corridas parciales.
  - `npm run build` de frontend en verde.

## Para que se hizo
- Permitir comparar proveedores (OpenAI vs Groq) dentro del mismo flujo funcional de creacion de items.
- Reducir riesgo de lock-in y habilitar experimentacion controlada por costo/rendimiento.
- Mantener compatibilidad de contrato backend aunque los modelos respondan de forma diferente.

## Que problemas se presentaron
- Diferencias de comportamiento entre modelos: Groq/Llama 4 genero respuestas no siempre alineadas al formato esperado.
- Casos reales de output con JSON parcialmente valido pero estructura interna incompatible con Tiptap (strings mezclados con nodos).
- Casos de contenido no deseado para el render actual (ej. salida tipo TikZ/LaTeX de graficos) que no se integra con el pipeline `media_spec`.
- Errores intermitentes de conectividad al proveedor (`Connection error`) durante pruebas directas.
- Percepcion de costo elevado al sumar reintentos/reparaciones y prompts extensos.

## Como se resolvieron
- Se introdujo capa de seleccion de proveedor/modelo por request para controlar explicitamente que motor se usa.
- Se mantuvo validacion de contrato backend como fuente de verdad, desacoplada del proveedor.
- Se agrego normalizacion defensiva del documento para recuperar outputs "casi correctos" sin romper frontend.
- Se configuro Structured Output en proveedor Groq con `json_schema` en modo `strict: false` para mejorar adherencia.
- Se mantuvo estrategia de retries y parseo resiliente para minimizar fallos por formato.
- Se dejo trazabilidad de uso (`usage`, `metadata.ai_model`, intentos de reparacion) para auditar costos y estabilidad.

## Que continua
- Afinar prompt por perfil de modelo/proveedor (no un unico prompt universal).
- Agregar guardrails especificos para bloquear salida no soportada (ej. TikZ) y forzar `media_specs`.
- Completar pruebas E2E comparativas OpenAI vs Groq con metricas (tasa de exito, retries, latencia, costo).
- Definir politica operativa por escenario: borrador rapido vs generacion estricta para guardado.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
