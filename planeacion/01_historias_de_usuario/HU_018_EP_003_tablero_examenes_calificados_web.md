# HU_018 - Tablero de examenes calificados en frontend web (EP_003)

## Trazabilidad
- Epica asociada: `EP_003_calificacion_omr_versionada_por_docente.md`
- Dependencias: `HU_008_EP_003_persistencia_resultados_y_evidencias_omr.md`

## Historia de usuario
**Como** docente o coordinador
**Quiero** ver en el frontend web los examenes calificados desde el movil
**Para** revisar resultados, evidencias e identificar casos que requieren revision manual.

## Criterios de aceptacion
1. Existe una pestaña "Examenes calificados" en el frontend web.
2. Se lista cada intento con columnas: Id examen, Version, Nombre examen, Estudiante, Grupo (si existe), Timestamp.
3. Cada fila permite abrir un detalle con:
   - respuestas correctas vs marcadas,
   - nivel de confianza por respuesta,
   - estado del intento,
   - imagen/evidencia del examen.
4. Si la informacion de grupo no existe en el modelo, la columna se muestra como "-" o se oculta.
5. El tablero consulta al backend y soporta paginacion basica si hay muchos intentos.

## Evidencia esperada
- UI web con tabla de intentos calificados.
- Endpoint backend consumido para listar intentos y sus metadatos.
- Vista de detalle con imagen/evidencias.

## Notas
- Esta HU no exige reportes estadisticos avanzados; se centra en consulta operativa.
