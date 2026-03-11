# Bitacora 037_03_11_2026 17:21:41 cierre_act_0046_ep002_postgres

## Que fue lo que se hizo
- Se ejecutó la validación de integración EP_002 sobre PostgreSQL con `tests/test_ep002_postgres_integration.py`.
- Se corrigió la prueba para ajustarla al contrato actual del endpoint `GET /api/v1/exams/{exam_id}/answer-key`, que retorna una lista estructurada y no un diccionario simple.
- Se corrigió el arranque del backend cuando `DEBUG` llega como texto de entorno (`release`, `prod`, `production`, `dev`, `development`).
- Se robusteció el flujo de migraciones para bases heredadas donde ya existen tablas pero el versionado de Alembic no está inicializado o está vacío.
- Archivos modificados:
  - `src/backend/tests/test_ep002_postgres_integration.py`
  - `src/backend/app/core/config.py`
  - `src/backend/app/db/migrations.py`

## Para que se hizo
- Cerrar formalmente la validación funcional de EP_002 en PostgreSQL.
- Evitar caídas de startup por parseo estricto de `DEBUG`.
- Evitar fallos de migración en escenarios reales de transición (tablas preexistentes sin versión Alembic).

## Que problemas se presentaron
- La prueba de integración falló porque esperaba un formato antiguo de `answer_key`.
- El backend falló en startup con `CalledProcessError` en migraciones; la causa raíz fue doble:
  - `DEBUG=release` no era interpretable como booleano por configuración.
  - Alembic intentó recrear tablas existentes al detectar estado base por `alembic_version` ausente/vacía.

## Como se resolvieron
- Se actualizó la aserción del test para validar el formato estructurado de `answer_key` y confirmar contenido por `question_number`.
- Se añadió normalización previa del valor `debug` en configuración para mapear cadenas comunes de entorno a booleanos válidos.
- Se encapsuló ejecución Alembic y se agregó detección de esquema legado:
  - Si existen tablas de dominio sin `alembic_version`, se ejecuta `stamp head`.
  - Si `alembic_version` existe pero no tiene filas y hay tablas de dominio, también se ejecuta `stamp head`.
  - Luego se ejecuta `upgrade head`.
- Con esto, el backend inició correctamente y la prueba EP_002 quedó en verde sobre PostgreSQL.

## Que continua
- Marcar `ACT_0046` como `DONE` en planeación, anexando evidencia de ejecución `1 passed`.
- Crear bitácora de cierre específica de actividad si se requiere separación por criterio documental.
- Continuar con la siguiente actividad de EP_004 (validación del flujo OMR versionado sobre PostgreSQL).

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
