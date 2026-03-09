estado: todo
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0041 - Integracion total E2E con dataset dummy

## Objetivo tecnico
Validar de punta a punta el flujo completo: creacion de cuestionario, clave de respuestas, lectura OMR movil, resolucion por `teacher_id + exam_code`, scoring y persistencia de resultado/evidencias.

## Tareas implementables
- [ ] Preparar dataset dummy reproducible (docente, examen, items y asociacion ordenada).
- [ ] Generar/validar clave de respuestas correcta por examen/version para el escenario de prueba.
- [ ] Ejecutar lectura OMR real desde modulo movil con identificacion de examen por OMR.
- [ ] Calificar intento contra examen/version resuelta por contexto de docente.
- [ ] Persistir intento, respuestas detalladas y artefactos tecnicos asociados.
- [ ] Consolidar reporte final E2E (entrada, salida, score y trazabilidad).

## Evidencias esperadas
- Escenario dummy documentado y repetible.
- Resultado E2E con score y detalle por pregunta.
- Evidencia de resolucion correcta de examen por `teacher_id + exam_code`.
- Evidencia de artefactos persistidos por intento (imagen/resultados auxiliares).

## Criterio de terminado
Existe una ejecucion integral comprobada que valida el flujo completo de aplicacion/calificacion OMR en contexto versionado por docente.
