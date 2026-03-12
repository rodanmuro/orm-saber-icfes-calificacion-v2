estado: todo
prioridad: alta
sprint: S6
owner: por_definir

# ACT_0051 - Endpoint y flujo web de importacion masiva GIFT

## Objetivo tecnico
Exponer endpoint de importacion GIFT y conectar la interfaz web para carga de archivo y visualizacion de resultados.

## Tareas implementables
- [ ] Crear endpoint `POST` para importar archivo `.gift` asociado a `teacher_id`.
- [ ] Persistir items validos y omitir items invalidos sin cortar el proceso completo.
- [ ] Implementar formulario de carga en frontend web.
- [ ] Mostrar resumen final (procesados, importados, errores).
- [ ] Crear pruebas de integracion API para importacion GIFT.

## Evidencias esperadas
- Flujo web funcional de carga de archivo GIFT.
- Items importados visibles en listado del banco.
- Evidencia de errores reportados por item.

## Criterio de terminado
Un docente puede subir un archivo GIFT e incorporar preguntas validas al banco de items con trazabilidad de errores.
