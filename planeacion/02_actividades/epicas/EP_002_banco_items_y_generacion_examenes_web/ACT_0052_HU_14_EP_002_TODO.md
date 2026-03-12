estado: todo
prioridad: media
sprint: S6
owner: por_definir

# ACT_0052 - Prevalidacion GIFT (analisis sin persistencia)

## Objetivo tecnico
Separar el analisis del archivo GIFT de la persistencia, permitiendo una fase de prevalidacion previa a confirmar importacion.

## Tareas implementables
- [ ] Implementar endpoint de analisis GIFT sin guardar en base de datos.
- [ ] Retornar lista de items validos y lista de errores con detalle.
- [ ] Definir identificador temporal de lote para confirmar posteriormente.
- [ ] Proteger expiracion y consistencia del lote temporal.
- [ ] Crear pruebas backend del flujo analizar->resultado.

## Evidencias esperadas
- Respuesta de prevalidacion con separacion clara validos/invalidos.
- Evidencia de que no hay persistencia en etapa de analisis.
- Pruebas de backend del flujo de prevalidacion en verde.

## Criterio de terminado
El sistema permite revisar calidad de importacion GIFT antes de guardar, con salida clara para decision del docente.
