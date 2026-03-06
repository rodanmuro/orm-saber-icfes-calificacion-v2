# EP_002 - Banco de items y generacion de examenes web

## Objetivo tecnico
Implementar un modulo web para docentes que permita crear, gestionar y versionar preguntas de seleccion multiple, armar examenes y generar versiones aplicables, manteniendo coherencia con el flujo OMR del proyecto.

## Alcance
- Crear frontend web separado (`src/frontend_web`) para authoring de preguntas.
- Crear y editar preguntas de seleccion multiple con enunciado y opciones A/B/C/D.
- Permitir asociar preguntas a referencias curriculares basicas (estandar/competencia) en modo inicial.
- Gestionar banco de items con busqueda y filtrado.
- Crear examenes asociados a docente.
- Asociar preguntas a examenes.
- Generar versiones de examen publicables (snapshot inmutable).
- Habilitar variacion de examen mediante:
  - cambio de orden de preguntas,
  - barajado de opciones por pregunta.
- Exportar examen a formato imprimible compatible con aplicacion OMR.

## Fuera de alcance
- Autenticacion/autorizacion completa.
- Analitica pedagogica avanzada.
- Motor de variantes parametrizables por familia de item (fase posterior).
- Integracion final con LMS externos.

## Entregables verificables
- App web funcional para gestion de items y examenes.
- API backend para CRUD de items, examenes y versiones.
- Modelo de datos inicial para banco de items y versiones de examen.
- Flujo reproducible para publicar una version de examen con orden/opciones definidos.
- Evidencia de exportacion de examen apto para aplicacion en hoja OMR.

## Restricciones tecnicas
- Backend unico en FastAPI.
- Frontend web desacoplado del frontend movil.
- Datos de examen versionados e inmutables al publicar.
- Persistencia de metadatos curriculares en modo liviano (Now-lite).

## Criterios de aceptacion
1. Un docente puede crear preguntas y almacenarlas en banco de items.
2. Un docente puede crear un examen y asociarle preguntas del banco.
3. El sistema puede publicar una version de examen con orden definido y opciones barajadas.
4. Dos versiones del mismo examen pueden diferir en orden de preguntas u opciones.
5. La salida exportada conserva trazabilidad de version para calificacion posterior.
