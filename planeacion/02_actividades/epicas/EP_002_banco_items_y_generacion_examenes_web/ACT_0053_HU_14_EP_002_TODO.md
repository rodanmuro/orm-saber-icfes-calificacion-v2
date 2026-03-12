estado: todo
prioridad: media
sprint: S6
owner: por_definir

# ACT_0053 - Confirmacion de importacion GIFT y UX de validacion

## Objetivo tecnico
Completar flujo de dos pasos para importacion GIFT con confirmacion explicita del docente y resumen final de ejecucion.

## Tareas implementables
- [ ] Implementar endpoint de confirmacion de lote validado.
- [ ] Persistir solo los items marcados como validos en la fase de preanalisis.
- [ ] Construir interfaz web de previsualizacion de items y errores.
- [ ] Mostrar resumen final de importados/omitidos y causas.
- [ ] Agregar pruebas E2E del flujo analizar->confirmar.

## Evidencias esperadas
- Flujo completo en web: analizar archivo, revisar, confirmar importacion.
- Persistencia selectiva de items validos.
- Evidencia de resumen final coherente con el analisis.

## Criterio de terminado
La importacion GIFT opera en dos fases controladas y evita ingreso accidental de items defectuosos al banco principal.
