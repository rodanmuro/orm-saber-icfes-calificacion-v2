estado: in_progress
prioridad: alta
sprint: S2
owner: por_definir

# ACT_0023 - Integracion de lector Gemini con salida estructurada

## Objetivo tecnico
Integrar un lector Gemini 1.5 Pro que procese imagen y devuelva respuestas en formato estructurado compatible con el backend.

## Tareas implementables
- [ ] Crear adaptador Gemini en backend con cliente y configuracion de modelo.
- [ ] Definir prompt tecnico de lectura OMR con formato de salida estricto.
- [ ] Validar/parsear respuesta con esquema tipado para evitar salidas invalidas.
- [ ] Manejar errores de red/cuota/timeout con respuesta controlada.

## Evidencias esperadas
- Modulo `gemini_reader` funcional en backend.
- Prueba manual de una imagen con respuesta estructurada valida.

## Criterio de terminado
El backend puede procesar al menos una imagen usando `gemini` y devolver JSON valido bajo el mismo contrato.
