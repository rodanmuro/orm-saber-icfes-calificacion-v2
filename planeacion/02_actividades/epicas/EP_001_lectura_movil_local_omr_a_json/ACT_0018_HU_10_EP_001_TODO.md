estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0018 - Comparacion de variantes y metricas base por imagen

## Objetivo tecnico
Comparar variantes de preprocesamiento con metricas objetivas para evaluar mejora de robustez.

## Tareas implementables
- [ ] Definir metrica comparativa minima por imagen (ambiguous_questions, blank_questions, separacion top1-top2).
- [ ] Ejecutar comparacion de variantes en lote de imagenes reales de `mobile_uploads`.
- [ ] Generar reporte estructurado (JSON/CSV) con resultados por imagen y variante.
- [ ] Identificar imagenes donde la nueva variante mejora o empeora.

## Evidencias esperadas
- Script/comando reproducible de comparacion.
- Reporte guardado en `data/output` con resumen por variante.

## Criterio de terminado
Existe un reporte reproducible que permite decidir con evidencia si la variante adicional aporta mejora neta.
