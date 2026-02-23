estado: todo
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0010 - Generacion de JSON de lectura por pregunta

## Objetivo tecnico
Construir salida JSON estructurada por `question_items` y opciones, con estados de marcacion y metadatos de calidad basicos.

## Tareas implementables
- [ ] Definir esquema de salida para lectura OMR local.
- [ ] Mapear resultados de burbujas a estructura por pregunta/opcion.
- [ ] Agregar metadatos minimos (`template_id`, `version`, `timestamp`, resumen de calidad).
- [ ] Validar consistencia entre cantidad esperada y cantidad reportada.

## Evidencias esperadas
- Archivo JSON de resultados generado por comando local.
- Documentacion corta del esquema de salida.

## Criterio de terminado
El JSON final representa todas las preguntas y opciones esperadas sin omisiones ni duplicados.
