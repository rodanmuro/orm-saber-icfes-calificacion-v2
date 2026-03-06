# HU_005 - Banco de items docente en frontend web (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Referencia funcional: Seccion 13 del fundacional (`planeacion/descripcion_fundacional_proyecto.md`)
- Referencia de planeacion: `bitacoras/028_02_28_2026_planeacion_decisiones_arquitectura_entidades_docente_examen.md`

## Historia de usuario
**Como** docente  
**Quiero** crear y gestionar preguntas de seleccion multiple desde una interfaz web  
**Para** construir un banco de items reutilizable para mis examenes.

## Criterios de aceptacion
1. Existe un frontend web separado del frontend movil para authoring de preguntas.
2. Puedo crear/editar preguntas con enunciado, opciones A/B/C/D y respuesta correcta.
3. Puedo registrar metadatos basicos de la pregunta (area, tema, dificultad y etiquetas curriculares basicas).
4. El banco permite consultar y filtrar preguntas por criterios basicos.
5. El backend persiste los items de forma versionable sin depender de autenticacion en este incremento.

## Evidencia esperada
- Frontend web base en `src/frontend_web`.
- Endpoints backend para CRUD de items.
- Persistencia de items en modelo estructurado.
- Evidencia de creacion y consulta de items desde UI web.

## Notas
- Alcance incremental en modo "lite": etiquetado curricular basico opcional en esta fase.
