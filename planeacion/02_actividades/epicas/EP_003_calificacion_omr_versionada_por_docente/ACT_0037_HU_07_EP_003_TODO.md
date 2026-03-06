estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0037 - Scoring OMR contra exam_version y option_map

## Objetivo tecnico
Aplicar calificacion OMR contra la clave correcta de la version publicada, respetando el mapeo de opciones barajadas por pregunta.

## Tareas implementables
- [ ] Implementar motor de scoring basado en `exam_version_item`.
- [ ] Aplicar `option_map` para convertir opcion marcada a dominio de respuesta correcta.
- [ ] Calcular puntaje total y detalle por pregunta.
- [ ] Incluir soporte para estados ambiguos/sin respuesta en calculo final.
- [ ] Agregar pruebas de regresion con versiones barajadas.

## Evidencias esperadas
- Resultado de scoring estructurado por intento y por pregunta.
- Casos de prueba con respuestas correctas/incorrectas bajo mapeos distintos.
- Evidencia de no regresion en flujo de lectura OMR actual.

## Criterio de terminado
La calificacion produce resultados correctos para versiones barajadas y mantiene comportamiento consistente en escenarios ambiguos.
