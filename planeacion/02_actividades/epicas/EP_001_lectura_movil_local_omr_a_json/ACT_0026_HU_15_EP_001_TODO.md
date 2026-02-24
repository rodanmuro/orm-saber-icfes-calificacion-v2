estado: todo
prioridad: media
sprint: S2
owner: por_definir

# ACT_0026 - Metricas operativas y controles de costo/latencia para Gemini

## Objetivo tecnico
Incorporar metricas operativas minimas para evaluar viabilidad de uso real del motor Gemini.

## Tareas implementables
- [ ] Medir y registrar latencia por solicitud en modo `gemini`.
- [ ] Registrar resultado final por solicitud (`ok`, `error_controlado`, `timeout`, `parse_error`).
- [ ] Consolidar resumen de costos estimados por lote de benchmark.
- [ ] Documentar limites operativos y recomendaciones de uso para MVP.

## Evidencias esperadas
- Salida de metricas operativas por corrida.
- Seccion documentada con riesgos y limites de operacion.

## Criterio de terminado
El equipo cuenta con visibilidad minima de costo/latencia/estabilidad para decidir adopcion de Gemini en siguientes sprints.
