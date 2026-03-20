estado: todo
prioridad: media
sprint: S7
owner: por_definir

# ACT_0059 - Trazabilidad, pruebas por capa y documentacion del modulo IA

## Objetivo tecnico
Asegurar auditabilidad del flujo IA, cobertura de pruebas por capa y documentacion para evolucion/extraibilidad del modulo.

## Tareas implementables
- [ ] Persistir metadata minima de origen IA al guardar item:
  - `ai_generated`, `ai_model`, `ai_prompt_version`.
- [ ] Implementar pruebas por capa:
  - unit tests del modulo `item_ai_assistant` (service/validators/prompt_builder)
  - tests de contrato del proveedor OpenAI (mock)
  - integration test del endpoint `POST /ai/generate-item`
  - E2E generar->aplicar->guardar item
- [ ] Documentar limites y responsabilidad de revision docente (no guardado automatico).
- [ ] Documentar arquitectura del modulo y estrategia de extraccion futura (servicio independiente).
- [ ] Actualizar README backend/frontend con configuracion `.env` requerida para IA.
- [ ] Verificar en pruebas que los guardrails no se puedan omitir (sin contexto, formato invalido, sin metadata IA).

## Evidencias esperadas
- Metadata IA visible y verificable en item persistido.
- Suite de pruebas del modulo y endpoint en verde.
- Documento tecnico de arquitectura modular y lineamientos operativos.

## Criterio de terminado
El modulo IA queda auditable, probado por capas y documentado con criterios claros para escalar o separar como servicio independiente.
