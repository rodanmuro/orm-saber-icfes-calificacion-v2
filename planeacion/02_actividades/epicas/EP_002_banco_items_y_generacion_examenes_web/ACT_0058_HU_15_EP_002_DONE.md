estado: done
prioridad: alta
sprint: S7
owner: por_definir

# ACT_0058 - UI mini chat IA en Editar item con integracion modular

## Objetivo tecnico
Incorporar en frontend un panel de chat IA que consuma el contrato del modulo `item_ai_assistant` y permita aplicar borradores al formulario sin persistencia automatica.

## Tareas implementables
- [x] Agregar componente de mini chat IA en la vista `Editar item`.
- [x] Integrar cliente frontend contra `POST /ai/generate-item`.
- [x] Habilitar generacion solo si `standard_name` y `competency_name` estan definidos.
- [x] Implementar `Aplicar al formulario` (enunciado/opciones/correcta) sin guardar automaticamente.
- [x] Aplicar automaticamente el borrador generado a enunciado/opciones/correcta, manteniendo guardado manual.
- [x] Mantener el flujo manual existente totalmente operativo.
- [x] Agregar estados de UX: loading, error, historial corto local.
- [x] Mostrar en UI tokens/costos por peticion IA (entrada, salida, cached y total USD).
- [x] Aplicar guardrails de interfaz: bloqueo por falta de contexto curricular y advertencia explicita de revision docente.

## Evidencias esperadas
- Flujo UI funcional: prompt -> respuesta -> aplicar.
- Validaciones de precondicion curricular visibles para usuario.
- Pruebas manuales de usabilidad y no-regresion del formulario.

## Criterio de terminado
El docente puede iterar con IA dentro de `Editar item` y transferir el borrador de forma controlada al formulario existente.
