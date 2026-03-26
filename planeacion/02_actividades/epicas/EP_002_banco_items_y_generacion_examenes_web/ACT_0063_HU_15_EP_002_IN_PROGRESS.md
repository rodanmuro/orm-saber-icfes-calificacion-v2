estado: en_progreso
prioridad: alta
sprint: S8
owner: por_definir

# ACT_0063 - Estabilizacion de contrato IA y regresion de salida estructurada

## Objetivo tecnico
Reducir errores de generacion en el asistente IA reforzando el contrato estructurado, la normalizacion de salida y la cobertura de pruebas de regresion.

## Tareas implementables
- [ ] Endurecer parseo de salida para tolerar ruido no estructurado alrededor del JSON.
- [ ] Homologar `media_spec` hacia un contrato interno unico (incluyendo variantes de entrada comunes).
- [ ] Mejorar validaciones de campos requeridos por tipo de grafica y mensajes de error orientados a accion.
- [ ] Agregar pruebas de regresion para casos reportados:
  - JSON invalido en respuesta del proveedor,
  - `media_spec` incompleto (`labels/values/sizes`),
  - texto con escapes de acentos.
- [ ] Agregar prueba de contrato del adaptador OpenAI con mock detallado de `usage` y salida.
- [ ] Documentar en backend limites actuales del contrato IA y recomendaciones de prompting operativo.

## Evidencias esperadas
- Disminucion de errores `HTTP 502` y `HTTP 422` en flujo de generacion IA.
- Suite de pruebas en verde para parseo y validacion de contrato.
- Documento tecnico actualizado con reglas de formato y limites actuales.

## Criterio de terminado
El asistente IA opera de manera estable en escenarios reales de uso docente, con errores controlados y diagnostico claro cuando el payload no cumple contrato.

