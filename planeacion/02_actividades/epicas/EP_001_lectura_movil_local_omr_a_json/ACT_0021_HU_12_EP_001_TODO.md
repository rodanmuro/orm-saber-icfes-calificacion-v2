estado: todo
prioridad: media
sprint: S2
owner: por_definir

# ACT_0021 - Senales de confianza y deuda tecnica de revision manual

## Objetivo tecnico
Definir y exponer senales de confianza por pregunta para preparar una fase futura de correccion manual asistida.

## Tareas implementables
- [ ] Definir metrica de margen por pregunta (top1-top2) y umbral de baja confianza.
- [ ] Exponer campo de baja confianza por pregunta en salida JSON.
- [ ] Agregar conteo global de preguntas de baja confianza en resumen.
- [ ] Documentar como esta senal alimentara el dashboard futuro de revision manual.

## Evidencias esperadas
- JSON de salida con campos de confianza por pregunta.
- Nota de deuda tecnica y plan de uso en frontend futuro.

## Criterio de terminado
El sistema entrega senales de confianza trazables por pregunta, listas para consumir en una futura interfaz de revision.
