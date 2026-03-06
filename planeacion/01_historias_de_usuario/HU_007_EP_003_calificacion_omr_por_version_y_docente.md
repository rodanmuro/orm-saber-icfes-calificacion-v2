# HU_007 - Calificacion OMR por version y docente (EP_003)

## Trazabilidad
- Epica asociada: `EP_003_calificacion_omr_versionada_por_docente.md`
- Referencia de dominio: `bitacoras/028_02_28_2026_planeacion_decisiones_arquitectura_entidades_docente_examen.md`

## Historia de usuario
**Como** sistema de calificacion  
**Quiero** resolver el examen en contexto de docente y version publicada  
**Para** calificar correctamente hojas OMR aun con barajado de preguntas/opciones.

## Criterios de aceptacion
1. El backend resuelve examen por clave de negocio `teacher_id + exam_code`.
2. La calificacion usa exclusivamente una `exam_version` publicada.
3. El scoring respeta el mapeo de opciones definido en la version aplicada.
4. Si no existe correspondencia docente+codigo+version, el sistema retorna error controlado y trazable.
5. El resultado mantiene estructura consistente para consumo del frontend movil.

## Evidencia esperada
- Flujo backend de resolucion de version de examen.
- Casos de prueba con versiones distintas de un mismo examen.
- Evidencia de calificacion correcta con opciones barajadas.

## Notas
- Esta HU no cubre autenticacion; asume contexto de docente provisto por capa de aplicacion.
