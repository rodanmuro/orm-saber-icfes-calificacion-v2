# HU_008 - Persistencia de resultados y evidencias OMR (EP_003)

## Trazabilidad
- Epica asociada: `EP_003_calificacion_omr_versionada_por_docente.md`
- Referencia tecnica: flujo actual de `omr_read` y artefactos en backend.

## Historia de usuario
**Como** docente y equipo tecnico  
**Quiero** que cada intento OMR guarde resultados, respuestas y evidencias tecnicas  
**Para** auditar calificaciones, revisar ambiguedades y mantener trazabilidad.

## Criterios de aceptacion
1. Cada intento OMR persiste identificadores de docente, estudiante (si aplica), examen/version y estado final.
2. Se guarda detalle por pregunta (respuesta marcada, correcta/incorrecta, ambiguedades).
3. Se guardan artefactos de evidencia (imagen original y salidas tecnicas relevantes).
4. Existe consulta estructurada por intento para auditoria y revision.
5. El sistema diferencia intentos validos, ambiguos y fallidos con estados claros.

## Evidencia esperada
- Modelo de datos para `omr_attempt`, `omr_attempt_answer`, `omr_attempt_artifact`.
- Endpoints de consulta de resultados por intento.
- Evidencia de trazabilidad completa sobre un intento real.

## Notas
- Esta HU habilita base para analitica posterior, pero no cubre dashboards avanzados en este incremento.
