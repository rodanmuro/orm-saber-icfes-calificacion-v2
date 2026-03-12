estado: todo
prioridad: alta
sprint: S6
owner: por_definir

# ACT_0050 - Parser backend para importacion GIFT de opcion multiple

## Objetivo tecnico
Implementar en backend un parser GIFT (alcance MVP) para preguntas de seleccion multiple y su mapeo al modelo de items.

## Tareas implementables
- [ ] Definir contrato de entrada para archivo `.gift`.
- [ ] Implementar parser de preguntas de opcion multiple (enunciado, opciones, correcta).
- [ ] Normalizar y mapear el resultado al modelo interno de item.
- [ ] Retornar errores por bloque/linea con causa legible.
- [ ] Agregar pruebas unitarias del parser con casos validos e invalidos.

## Evidencias esperadas
- Parser funcional con cobertura minima para casos felices y errores comunes.
- Reporte estructurado de importacion (procesados, validos, invalidos).
- Suite de pruebas del parser ejecutada correctamente.

## Criterio de terminado
El backend interpreta archivos GIFT de opcion multiple y produce una estructura confiable para persistencia de items.
