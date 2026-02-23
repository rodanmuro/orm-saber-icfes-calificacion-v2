estado: todo
prioridad: media
sprint: S2
owner: por_definir

# ACT_0011 - Evaluacion de precision con set de fotos reales

## Objetivo tecnico
Implementar un flujo de evaluacion sobre fotos diligenciadas para medir precision inicial de lectura OMR.

## Tareas implementables
- [ ] Definir estructura de dataset local (imagen + esperado).
- [ ] Implementar comparador de salida leida vs verdad esperada.
- [ ] Calcular metricas basicas de precision (por burbuja y por pregunta).
- [ ] Generar reporte resumen reproducible.

## Evidencias esperadas
- Script/CLI para evaluar lote de fotos.
- Reporte de precision con resultados observables.

## Criterio de terminado
Existe metrica objetiva de desempeno del lector sobre un set minimo de fotos reales de prueba.
