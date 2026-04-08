# Bitacora 054_04_08_2026 exportacion_pdf_letter_y_docx_dos_columnas

## Que fue lo que se hizo
- Se corrigieron dos bugs en `src/backend/app/modules/exam_export/pdf_service.py`:
  - Se agregó la importación faltante `from reportlab.lib import colors`, que causaba `NameError` al renderizar tablas.
  - Se renombró la variable `row` a `matrix_row` en el bloque `except` del renderizado de tablas para evitar solapamiento con la variable `row` del loop externo `for row in version_items`.
- Se cambió el tamaño de página del PDF de A4 a Letter (`LETTER`) en `pdf_service.py`.
- Se creó el nuevo servicio `src/backend/app/modules/exam_export/docx_service.py` para generación de cuadernillos en formato Word:
  - Tamaño carta (8.5" x 11"), márgenes 0.5".
  - Dos columnas con gutter de 0.3" configuradas via XML de sección (`<w:cols w:num="2" w:space="432"/>`).
  - Renderiza enunciado y opciones A/B/C/D por pregunta soportando texto, imágenes PNG, ecuaciones LaTeX (vía matplotlib igual que el PDF) y tablas.
  - Anchos de imagen limitados al ancho de columna (`COLUMN_WIDTH_IN ≈ 3.6"`).
- Se agregó el endpoint `GET /api/v1/exams/{exam_id}/versions/{version_id}/export/docx` en `src/backend/app/api/v1/endpoints/exams.py`.
- Se agregó `python-docx==1.2.0` a `src/backend/requirements.txt` y se instaló en el entorno virtual.

## Para que se hizo
- Proveer exportación del cuadernillo de examen en formato Word editable, como alternativa al PDF.
- Alinear el formato de impresión del PDF al tamaño carta estándar usado en Colombia.
- Corregir el fallo silencioso que devolvía `Internal Server Error` (21 bytes) al exportar exámenes que contenían ítems con tablas.

## Que problemas se presentaron
- El endpoint PDF devolvía `Internal Server Error` en lugar del PDF cuando algún ítem tenía tablas en el enunciado u opciones. Las primeras exportaciones funcionaban porque los ítems solo tenían imágenes; en cuanto apareció un ítem con tabla, el servidor fallaba.
- Al crear `docx_service.py` con `from docx.util import Emu` (módulo inexistente en python-docx 1.2.0), uvicorn en modo reload entró en un ciclo de reinicios que dejó todos los endpoints colgados, incluyendo el PDF.
- El primer DOCX generado salía en una sola columna porque la configuración de columnas no se había implementado.

## Como se resolvieron
- **`colors` faltante**: se agregó `from reportlab.lib import colors` al inicio de `pdf_service.py`. La causa raíz fue que el código de renderizado de tablas referenciaba `colors.black` y `colors.HexColor(...)` sin importar el módulo.
- **Servidor colgado**: se identificó que `from docx.util import Emu` lanzaba `ModuleNotFoundError` en tiempo de importación. Se corrigió moviendo `Emu` al import correcto: `from docx.shared import Emu, Inches, Pt, RGBColor`.
- **DOCX una sola columna**: se agregó configuración XML de sección en `_set_page_size_letter()` usando `OxmlElement("w:cols")` con `w:num="2"` y `w:space` de 432 twips (0.3"). Word fluye el contenido automáticamente entre columnas.

## Que continua
- Mejorar la fidelidad visual del DOCX: estilos de fuente, espaciado entre preguntas y jerarquía tipográfica.
- Evaluar si agregar encabezado/pie de página con nombre del examen y numeración de páginas.
- Exponer ambos endpoints (`/export/pdf` y `/export/docx`) desde el frontend web en la sección de armado de examen.
- Validar comportamiento con ítems que combinan imagen + ecuación + tabla en el mismo enunciado.

*(Archivos clave: `src/backend/app/modules/exam_export/pdf_service.py`, `src/backend/app/modules/exam_export/docx_service.py`, `src/backend/app/api/v1/endpoints/exams.py`)*
