# Bitacora 071_05_22_2026 10:42:29 filtros_analiticas_informe_estudiante

## Que fue lo que se hizo
- Se ampliaron los filtros de `Analiticas` en `src/frontend_web/src/components/AnalyticsPanel.jsx`.
- Se agrego filtrado local en `Resultados por pregunta` por numero de pregunta e `ID item`, con soporte para multiples valores separados por comas.
- Se cambiaron los filtros globales de `Codigo examen` y `Grupo` a seleccion multiple visible en `src/frontend_web/src/components/AnalyticsPanel.jsx`.
- Se ajusto `src/frontend_web/src/App.jsx` para que `analyticsFilters` use arreglos y el filtrado de intentos analiticos se haga por pertenencia a multiples codigos/grupos.
- Se agrego un bloque de `Informe por estudiante` con busqueda por nombre o numero de documento y tabla de examenes presentados.
- Se separo la fuente de datos del informe por estudiante para que consulte todos los intentos cargados, mientras ranking y resumen siguen dependiendo de los filtros globales.
- Se agrego `Codigo OMR` al informe por estudiante.
- Se actualizo `src/backend/app/api/v1/endpoints/omr_read.py` para incluir `student_document_number` y `student_document_type` en el listado base de intentos.

## Para que se hizo
- Permitir analisis mas fino por pregunta especifica o conjunto de preguntas/items.
- Habilitar seleccion multiple de examenes y grupos sin exigir que el usuario recuerde los valores disponibles.
- Dar visibilidad del historial de examenes presentados por un estudiante puntual desde el modulo de analiticas.

## Que problemas se presentaron
- El informe por estudiante inicialmente quedaba afectado por los filtros globales de analiticas, lo cual no correspondia al objetivo funcional.
- El listado base de intentos no traia el numero de documento del estudiante, por lo que la busqueda por documento no era fiable.
- Una validacion inicial del backend con `python -m py_compile` fallo porque en el entorno el binario disponible es `python3`.

## Como se resolvieron
- Se incorporo un estado local para filtros de preguntas y se aplico sobre `questionStats` antes del ordenamiento y de la grafica.
- Se paso `analyticsFilters` de strings a arreglos y se reemplazo la comparacion simple por inclusion en listas seleccionadas.
- Se uso `select multiple` para `Codigo examen` y `Grupo`, con limpieza explicita de seleccion.
- Se introdujo la prop `allAttempts` hacia `AnalyticsPanel` para desacoplar el informe por estudiante de los filtros globales.
- Se extendio el endpoint `list_omr_attempts` para exponer `student_document_number`, evitando depender del detalle individual del intento.
- La verificacion backend se repitio con `python3 -m py_compile`, y el frontend se valido repetidamente con `npm run build`.

## Que continua
- Evaluar si el informe por estudiante necesita exportacion CSV o PDF.
- Revisar si conviene reemplazar el `select multiple` por un selector con chips o busqueda integrada para mejorar UX cuando crezcan las listas.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
