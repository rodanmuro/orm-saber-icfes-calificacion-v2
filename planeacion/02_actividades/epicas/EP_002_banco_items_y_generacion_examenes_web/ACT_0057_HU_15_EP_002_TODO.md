estado: todo
prioridad: alta
sprint: S7
owner: por_definir

# ACT_0057 - Modulo backend IA desacoplado para generacion de items

## Objetivo tecnico
Implementar un modulo interno aislado de generacion de items con IA (`item_ai_assistant`), con endpoint HTTP delgado y adaptador OpenAI intercambiable.

## Tareas implementables
- [ ] Crear modulo `app/modules/item_ai_assistant/` con separacion por capas:
  - `domain` (contratos/DTOs)
  - `service` (caso de uso generar borrador)
  - `prompt_builder` (plantilla/version de prompt)
  - `validators` (reglas de formato)
  - `providers/openai_provider.py` (adaptador OpenAI)
- [ ] Definir interfaz de proveedor LLM (`LLMProvider`) para desacoplar la logica de negocio del SDK de OpenAI.
- [ ] Crear endpoint `POST /ai/generate-item` como adaptador HTTP (sin logica de negocio embebida).
- [ ] Definir contrato de entrada/salida estructurado para frontend.
- [ ] Implementar manejo de errores y timeouts sin exponer detalles internos del proveedor.
- [ ] Aplicar guardrails de backend: salida estricta A/B/C/D, una sola correcta, y rechazo de payload invalido.

## Evidencias esperadas
- Estructura modular creada y usada por endpoint.
- Endpoint funcional con salida estructurada valida.
- Pruebas unitarias del servicio y validadores con proveedor mock.

## Criterio de terminado
La generacion IA de items funciona en backend con un modulo desacoplado, testeable y potencialmente extraible a servicio independiente.
