estado: blocked
prioridad: media
sprint: S2
owner: por_definir

# ACT_0019 - Seleccion automatica de variante por metricas

## Objetivo tecnico
Implementar una regla determinista para seleccionar automaticamente la variante de lectura mas estable por imagen.

## Tareas implementables
- [ ] Definir regla de seleccion (prioridad: menos ambiguas; desempate: mayor margen top1-top2).
- [ ] Integrar la regla al pipeline para elegir variante ganadora.
- [ ] Exponer en diagnosticos la variante seleccionada y metricas de decision.
- [ ] Validar con lote de imagenes que la seleccion no degrada casos actualmente estables.

## Evidencias esperadas
- Codigo backend con selector automatico.
- Salida JSON con campo de variante activa y metricas asociadas.

## Criterio de terminado
El pipeline selecciona variante automaticamente con trazabilidad clara de la decision y resultados consistentes.

## Estado de pausa
- Actividad pausada temporalmente por priorizacion del enfoque de motor alterno LLM (Gemini).
- Se reactivara al cerrar HU_003 (ACT_0022+).
