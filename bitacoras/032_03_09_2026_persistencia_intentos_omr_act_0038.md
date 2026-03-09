# Bitacora 032_03_09_2026 17:27:24 persistencia_intentos_omr_act_0038

## Que fue lo que se hizo
- Se implemento un primer bloque de `ACT_0038` para persistir intentos OMR y detalle por pregunta.
- Se agregaron entidades de dominio en backend:
  - `OmrAttempt`
  - `OmrAttemptAnswer`
  en `src/backend/app/db/models.py`.
- Se registro export de modelos en `src/backend/app/db/__init__.py`.
- Se agrego migracion SQL:
  - `src/backend/migrations/0003_omr_attempt_and_answers.sql`.
- Se creo modulo de persistencia para scoring/lectura:
  - `src/backend/app/modules/omr_scoring/persistence.py`.
- Se integro persistencia al endpoint `POST /api/v1/omr/read-photo`:
  - guarda intento y respuestas detalladas al finalizar lectura/calificacion,
  - devuelve `diagnostics.attempt_id`.
- Se agrego endpoint de consulta de intento para auditoria basica:
  - `GET /api/v1/omr/attempts/{attempt_id}`
  en `src/backend/app/api/v1/endpoints/omr_read.py`.
- Se actualizo documentacion backend en `src/backend/README.md`.

## Para que se hizo
- Dar trazabilidad formal por intento OMR dentro de EP_003.
- Preparar el flujo E2E para consultar resultado historico por `attempt_id`.
- Desacoplar lectura/calificacion del almacenamiento estructurado de resultados.

## Que problemas se presentaron
- Riesgo de sobreacoplar el endpoint `read-photo` con logica de persistencia y scoring.
- Necesidad de manejar casos sin resolucion de examen (modo solo lectura) sin perder detalle.

## Como se resolvieron
- Se separo la persistencia en modulo dedicado (`omr_scoring/persistence.py`).
- Se definio estrategia de estado por intento:
  - `graded` cuando hay resolucion+scoring,
  - `resolution_error` cuando falla resolucion,
  - `read_only` cuando no aplica grading.
- Se implemento fallback para registrar respuestas detectadas aun sin clave de respuestas.
- Se agregaron pruebas unitarias para validar persistencia/summary basico:
  - `src/backend/tests/test_omr_attempt_persistence.py`.

## Que continua
- Continuar con `ACT_0039`: entidad formal de artefactos por intento (`omr_attempt_artifact`).
- Completar cierre de `ACT_0038` con pruebas de integracion HTTP y evidencia de consultas por intento/examen.
- Ejecutar escenario dummy integral (`ACT_0041`) con lectura movil + scoring + persistencia completa.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
