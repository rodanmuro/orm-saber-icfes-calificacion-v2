estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0025 - Benchmark comparativo classic vs gemini por lote de imagenes

## Objetivo tecnico
Crear un benchmark reproducible sobre `mobile_uploads` para comparar ambos motores con la misma verdad-terreno.

## Tareas implementables
- [ ] Definir formato de entrada con respuestas esperadas por pregunta.
- [ ] Ejecutar lectura por lote con `classic` y `gemini`.
- [ ] Calcular metricas por imagen: exactitud, vacias, ambiguas, errores de procesamiento.
- [ ] Guardar reporte consolidado en `JSON` y/o `CSV`.

## Evidencias esperadas
- Script/comando de benchmark reproducible.
- Reporte por imagen y resumen global por motor.

## Criterio de terminado
Existe un benchmark automatizado que produce comparacion objetiva entre ambos motores.
