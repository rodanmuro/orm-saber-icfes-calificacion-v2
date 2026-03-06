# EP_003 - Calificacion OMR versionada por docente

## Objetivo tecnico
Extender el flujo de calificacion OMR para evaluar hojas contra versiones publicadas de examen, resolviendo la identificacion de examen en contexto de docente y persistiendo resultados, respuestas y evidencias.

## Alcance
- Definir modelo de dominio de evaluacion con entidades:
  - docente,
  - estudiante (UUID + documento),
  - examen,
  - version de examen,
  - intento OMR,
  - respuestas por intento,
  - artefactos de evidencia.
- Resolver examen por clave de negocio `teacher_id + exam_code`.
- Calificar respuestas OMR contra clave correcta de la version aplicada.
- Soportar calificacion valida cuando existe barajado de opciones por version.
- Persistir:
  - puntaje,
  - respuestas marcadas,
  - ambiguedades,
  - rutas de artefactos (imagen, result.json, ratios).
- Mantener compatibilidad del flujo actual de lectura OMR como base tecnica.

## Fuera de alcance
- Motor antifraude avanzado.
- Analitica longitudinal institucional.
- Integracion con autenticacion federada.
- Automatizacion de reportes curriculares avanzados.

## Entregables verificables
- Esquema de datos inicial de calificacion versionada.
- API backend para registrar intentos y consultar resultados.
- Flujo backend de calificacion por version de examen.
- Persistencia de trazabilidad por intento OMR.
- Casos de prueba de calificacion correcta con versiones distintas del mismo examen.

## Restricciones tecnicas
- La calificacion se ejecuta contra una version publicada, no contra examen editable.
- El identificador OMR de examen se interpreta en contexto de docente.
- Debe conservarse trazabilidad de evidencias por intento.
- Debe mantenerse desacople entre motor de lectura (deteccion) y capa de scoring/persistencia.

## Criterios de aceptacion
1. Dado un intento OMR valido, el backend identifica la version de examen correspondiente en contexto de docente.
2. El sistema calcula y persiste puntaje y detalle por pregunta.
3. La calificacion funciona aun cuando las opciones fueron barajadas en la version aplicada.
4. Se almacenan evidencias tecnicas del intento para auditoria.
5. El resultado puede consultarse de forma estructurada por intento y por examen/version.
