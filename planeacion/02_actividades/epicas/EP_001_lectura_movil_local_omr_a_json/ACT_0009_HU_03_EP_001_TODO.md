estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0009 - Clasificacion de burbujas por ROI

## Objetivo tecnico
Implementar evaluacion de burbujas sobre imagen corregida para clasificar `marcada` o `no_marcada` con criterio reproducible.

## Tareas implementables
- [ ] Implementar extraccion de ROI por burbuja usando metadatos de plantilla.
- [ ] Definir metrica de relleno/oscurecimiento por ROI.
- [ ] Implementar regla de umbral parametrizable para clasificacion binaria.
- [ ] Gestionar estado ambiguo cuando se detecte borde de decision (si aplica).

## Evidencias esperadas
- Modulo de lectura de burbujas en `src/backend`.
- Salida intermedia con metricas por burbuja para depuracion.

## Criterio de terminado
Todas las burbujas se evalúan exactamente una vez con clasificacion reproducible y trazable.
