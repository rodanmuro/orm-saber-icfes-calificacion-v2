# Bitacora 042_03_20_2026 18:30:31 planeacion_modulo_ia_guardrails

## Que fue lo que se hizo
- Se evaluo la propuesta de tratar la generacion de preguntas con IA como modulo aislado y no como logica mezclada en endpoints existentes.
- Se definio que no se creara epica nueva; la iniciativa queda dentro de `EP_002_banco_items_y_generacion_examenes_web`.
- Se ajustaron actividades para reflejar arquitectura modular desacoplada y extraible:
  - `ACT_0057_HU_15_EP_002_TODO.md`
  - `ACT_0058_HU_15_EP_002_TODO.md`
  - `ACT_0059_HU_15_EP_002_TODO.md`
- Se reforzaron guardrails en la historia de usuario `HU_015_EP_002_asistente_ia_generacion_items.md`.

### Archivos modificados
- `planeacion/01_historias_de_usuario/HU_015_EP_002_asistente_ia_generacion_items.md`
- `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0057_HU_15_EP_002_TODO.md`
- `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0058_HU_15_EP_002_TODO.md`
- `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0059_HU_15_EP_002_TODO.md`

## Para que se hizo
- Garantizar que el asistente IA de generacion de items sea testeable, aislable y escalable desde su primera iteracion.
- Evitar acoplamiento de logica de negocio IA con controladores HTTP y UI de formulario.
- Dejar trazabilidad formal de los guardrails de seguridad y calidad antes de iniciar implementacion.

## Que problemas se presentaron
- Riesgo de acoplar la logica IA en el endpoint y en la vista de edicion, dificultando pruebas unitarias y futura extraccion como servicio.
- Riesgo de omitir controles operativos (guardrails) al implementar solo con enfoque funcional de corto plazo.

## Como se resolvieron
- Se ajusto la planeacion para forzar arquitectura por capas en backend (`item_ai_assistant` con dominio, servicio, prompt builder, validadores y proveedor OpenAI desacoplado).
- Se definio endpoint delgado (`POST /ai/generate-item`) como adaptador, sin logica central incrustada.
- Se incorporaron guardrails explicitos en HU y actividades:
  - no guardado automatico de items generados por IA,
  - bloqueo de generacion sin `standard_name` y `competency_name`,
  - salida estricta (A/B/C/D, una correcta),
  - trazabilidad obligatoria en metadata (`ai_generated`, `ai_model`, `ai_prompt_version`),
  - manejo de errores controlado sin romper el flujo manual.

## Que continua
- Iniciar implementacion de `ACT_0057` (modulo backend IA desacoplado).
- Continuar con `ACT_0058` (mini chat IA en `Editar item`) y `ACT_0059` (trazabilidad/pruebas/documentacion).
- Ejecutar pruebas por capa antes de habilitar uso operativo del asistente IA.

*(Referencias clave: HU_015, ACT_0057, ACT_0058, ACT_0059)*
