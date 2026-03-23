estado: en_progreso
prioridad: media
sprint: S7
owner: por_definir

# ACT_0059 - Trazabilidad, pruebas por capa y documentacion del modulo IA

## Objetivo tecnico
Asegurar auditabilidad del flujo IA, cobertura de pruebas por capa y documentacion para evolucion/extraibilidad del modulo.

## Tareas implementables
- [x] Persistir metadata minima de origen IA al guardar item:
  - `ai_generated`, `ai_model`, `ai_prompt_version`.
- [x] Implementar pruebas por capa:
  - unit tests del modulo `item_ai_assistant` (service/validators/prompt_builder)
  - integration test del endpoint `POST /ai/generate-item`
- [x] Robustecer parseo de salida IA para tolerar ruido de texto antes/despues del JSON.
- [x] Normalizar variantes de `media_spec` (`data`, `values`, `sizes`) al contrato interno esperado.
- [ ] Agregar test de contrato especifico del proveedor OpenAI (mock detallado de usage/output).
- [ ] Implementar E2E generar->aplicar->guardar item.
- [ ] Documentar limites y responsabilidad de revision docente (no guardado automatico).
- [ ] Documentar arquitectura del modulo y estrategia de extraccion futura (servicio independiente).
- [ ] Actualizar README backend/frontend con configuracion `.env` requerida para IA y bloque de costos/tokens.
- [x] Verificar en pruebas que los guardrails no se puedan omitir (sin contexto y formato invalido).

## Evidencias esperadas
- Metadata IA visible y verificable en item persistido.
- Suite de pruebas del modulo y endpoint en verde.
- Documento tecnico de arquitectura modular y lineamientos operativos.

## Criterio de terminado
El modulo IA queda auditable, probado por capas y documentado con criterios claros para escalar o separar como servicio independiente.
