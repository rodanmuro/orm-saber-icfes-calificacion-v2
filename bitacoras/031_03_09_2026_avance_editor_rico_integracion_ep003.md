# Bitacora 031_03_09_2026 17:01:17 avance_editor_rico_integracion_ep003

## Que fue lo que se hizo
- Se implemento editor enriquecido en `src/frontend_web` usando Tiptap para enunciado y opciones A/B/C/D.
- Se agrego soporte de ecuaciones LaTeX (KaTeX) mediante nodo `mathInline` y accion `fx` en toolbar:
  - `src/frontend_web/src/editor/MathInline.jsx`
  - `src/frontend_web/src/components/RichTextEditor.jsx`
  - `src/frontend_web/src/main.jsx`
- Se agrego soporte de imagenes en editor con upload real a backend:
  - frontend: `src/frontend_web/src/api/assetsApi.js`
  - backend upload: `src/backend/app/api/v1/endpoints/assets.py`
  - registro de ruta: `src/backend/app/api/v1/router.py`
  - publicacion estaticos: `src/backend/app/main.py` (mount `/assets`).
- Se actualizo formulario/listado para compatibilidad de contenido serializado (JSON string):
  - `src/frontend_web/src/components/ItemForm.jsx`
  - `src/frontend_web/src/components/ItemList.jsx`
  - `src/frontend_web/src/utils/editorDoc.js`
  - `src/frontend_web/src/styles.css`.
- Se avanzo integracion de EP_003 en backend:
  - endpoint de clave de respuestas `GET /api/v1/exams/{exam_id}/answer-key` en `src/backend/app/api/v1/endpoints/exams.py`.
  - modulo de scoring `src/backend/app/modules/omr_scoring/service.py`.
  - extension de `POST /api/v1/omr/read-photo` para resolver `teacher_id + exam_code` y retornar bloque `grading`.
- Se actualizo planeacion para dejar explicita la parte de editor enriquecido:
  - HU actualizada: `planeacion/01_historias_de_usuario/HU_005_EP_002_banco_items_docente_web.md`
  - nueva actividad: `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0040_HU_05_EP_002_TODO.md`
  - nueva actividad E2E de EP_003: `planeacion/02_actividades/epicas/EP_003_calificacion_omr_versionada_por_docente/ACT_0041_HU_08_EP_003_TODO.md`.

## Para que se hizo
- Habilitar authoring real de preguntas con contenido mas cercano a uso academico (texto rico, ecuaciones e imagenes).
- Preparar el flujo de integracion total de calificacion (resolucion de examen + scoring) en contexto de docente.
- Dejar trazabilidad de planificacion para continuar mejoras UX y cierre de E2E.

## Que problemas se presentaron
- Fallos intermitentes de red al instalar dependencias npm del editor (`ENOTFOUND registry.npmjs.org`).
- Build inicial fallida por import de KaTeX sin dependencia instalada.
- Entorno de pruebas del agente con cuelgues intermitentes de `TestClient` en algunos tests de integracion HTTP.

## Como se resolvieron
- Se reintento instalacion de dependencias npm con permisos escalados y se completo correctamente.
- Se incluyeron dependencias faltantes (`katex`, extensiones Tiptap) y se valido compilacion final.
- Se uso validacion automatica estable por `py_compile` y prueba unitaria dedicada de scoring:
  - `src/backend/tests/test_omr_grading_service.py` -> `1 passed`.
- Se valido frontend con build productivo:
  - `cd src/frontend_web && npm run build` -> `✓ built`.

## Que continua
- Cerrar formalmente ACT_0040 con validacion manual de ecuaciones e imagenes en UI.
- Continuar EP_003 con persistencia de intentos OMR (`ACT_0038`) y artefactos (`ACT_0039`).
- Ejecutar escenario dummy E2E completo (`ACT_0041`) y consolidar reporte final de integracion.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
