# Bitacora 024_02_24_2026 22:46:47 incidencia_coherencia_pdf_json_y_decision_pipeline

## Que fue lo que se hizo
- Se investigó una incidencia crítica de lectura OMR en plantilla v2: algunos bloques se leían bien (identidad/examen), mientras otros fallaban (documento/respuestas).
- Se verificó con pruebas determinísticas que existía desfase geométrico entre el PDF impreso y el metadata JSON usado por el lector.
- Se comprobó que el PDF validado en pruebas de campo estaba siendo generado por `generate_layout_wireframe.py`, mientras el JSON de lectura venía del pipeline `generate_template.py`.
- Se creó un flujo nuevo de render desde metadata para validar coherencia 1:1:
  - `src/backend/app/modules/template_generator/scripts/generate_pdf_from_metadata.py`
- Se creó flujo paralelo para generar metadata wireframe sin tocar v2 original:
  - `src/backend/app/modules/template_generator/scripts/generate_wireframe_metadata.py`
  - salida: `src/backend/data/output/template_basica_omr_v2_wireframe.json`
  - PDF asociado: `src/backend/data/output/template_basica_omr_v2_wireframe.pdf`
- Se ajustó el backend para usar solo metadata de backend (no depender del front para `metadata_path`) y fijar por configuración el metadata wireframe.

## Para que se hizo
- Eliminar incoherencias entre lo que se imprime y lo que el lector OMR interpreta.
- Evitar que el front controle una ruta de metadata en producción, reduciendo riesgo de errores operativos.
- Aislar la solución en un artefacto nuevo (`*_wireframe`) sin romper el v2 anterior.

## Que problemas se presentaron
- Desfase parcial de coordenadas: `document_type` y `respuestas` no coincidían con la impresión, aunque otras zonas sí.
- Confusión por coexistencia de dos pipelines con geometría distinta:
  - `generate_template.py` (pipeline oficial config -> layout -> pdf/json)
  - `generate_layout_wireframe.py` (script de diseño/prototipo)
- `generate_template.py` no acepta metadata exportada como entrada, porque espera un `TemplateConfig` (estructura distinta).

## Como se resolvieron
- Se confirmó técnicamente que la causa raíz era “pipeline cruzado” (PDF y JSON de rutas distintas).
- Se dejó explícito que `generate_template.py` **no es compatible directamente** con metadata JSON porque su contrato de entrada es config (`page_config`, `aruco_config`, `block_config`, `bubble_config`, `output_config`), no metadata (`question_items`, `aruco_markers`, etc.).
- Se implementó un renderizador “metadata -> PDF” para validar coherencia exacta con la lectura.
- Se creó metadata wireframe derivada del layout validado para pruebas reales sin tocar v2 original.
- Se fijó backend-only metadata por configuración, ignorando `metadata_path` enviado por front cuando difiere.

## Que continua
- Decision tomada (actual): mantener `template_basica_omr_v2_wireframe.json` + `template_basica_omr_v2_wireframe.pdf` como carril de validación funcional.
- Respuesta a pregunta “dejar nuevo modo como fuente de verdad JSON”:
  - Sí para esta fase de estabilización, porque garantiza coherencia con el lector.
- Respuesta a pregunta “por qué `generate_template.py` no es compatible directo con JSON metadata”:
  - Porque `generate_template.py` opera sobre esquema de configuración y recalcula layout; metadata ya es resultado final, no entrada de ese pipeline.
- Respuesta a pregunta “opción más mantenible y escalable”:
  - Opción recomendada: **un solo pipeline oficial** con un único esquema fuente y generación conjunta PDF+JSON.
  - Estado transitorio: usar metadata como fuente de verdad para lectura y para render de validación, mientras se migra el layout wireframe al pipeline oficial.
- Siguiente actividad técnica:
  - Unificar definitivamente en un solo pipeline (eliminar duplicidad wireframe vs renderer base) y agregar validación automática de coherencia antes de publicar plantillas.

*(Archivos clave: `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`, `src/backend/app/modules/template_generator/scripts/generate_pdf_from_metadata.py`, `src/backend/app/modules/template_generator/scripts/generate_wireframe_metadata.py`, `src/backend/data/output/template_basica_omr_v2_wireframe.json`, `src/backend/data/output/template_basica_omr_v2_wireframe.pdf`, `src/backend/app/api/v1/endpoints/omr_read.py`, `src/backend/app/core/config.py`.)*
