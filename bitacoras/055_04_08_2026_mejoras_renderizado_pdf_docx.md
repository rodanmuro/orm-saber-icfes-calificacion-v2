# Bitacora 055_04_08_2026 mejoras_renderizado_pdf_docx

## Que fue lo que se hizo
- Se refactorizó el renderizado de párrafos en `pdf_service.py`:
  - Se reemplazó `_node_to_text_parts` / `_doc_to_text_and_images` por `_build_inline_markup` + `_render_tiptap_doc`, que preserva el orden inline de texto, `mathInline` e imágenes dentro del mismo párrafo usando markup `<img valign="middle"/>` de ReportLab.
  - Se agregó `_merge_inline_image_paragraphs`: fusiona párrafos de imagen pequeña (alto < 160px) con el párrafo de texto anterior para renderizarlos inline.
  - Se agregó manejo explícito de nodos `image` a nivel top del doc (no dentro de `paragraph`) como bloque.
  - Se reemplazó `_table_as_matrix` por `_table_as_paragraph_matrix`: celdas con `Paragraph` que soportan `mathInline` renderizado como imagen inline.
  - Se eliminó `spaceAfter` en el estilo `ExamBody` (puesto a 0) y los `Spacer` entre imágenes.
  - Se corrigió el prefijo `A.`/`B.`/`C.`/`D.` en opciones cuyo doc es imagen a nivel top.
- Se refactorizó `docx_service.py` con los mismos principios:
  - `_render_paragraph_node` crea un único párrafo Word con runs múltiples en secuencia (texto, `mathInline`, imágenes inline y bloque).
  - `_merge_inline_image_paragraphs` aplicada también en DOCX.
  - `_add_table_node` reescrita con anchos de columna explícitos (`w:tblW`, `w:tcW` en twips), detección de filas header, y `_fill_cell_content` que renderiza `mathInline` como imagen en cada celda.
  - `_no_spacing` aplicada a todos los párrafos de contenido para eliminar espacio antes/después.
  - `_add_picture_no_border` / `_remove_image_border`: quita el `<a:ln>` del `pic:spPr` y agrega `<a:ln><a:noFill/>` para eliminar bordes de imágenes inline.
  - `_collect_plain_text` actualizada para extraer el latex limpio de `mathInline`.
- Se corrigió strip de delimitadores `$$...$$` (doble dólar) en `_render_latex_to_png` usando `while` en lugar de `if`, tanto en PDF como en DOCX. Esto resolvía que la opción A del ítem 143 no se renderizara.
- Se agregó prefijo `A.`/`B.`/`C.`/`D.` en opciones cuyo contenido es imagen pura (ítem 114 y similares).
- Archivos modificados:
  - `src/backend/app/modules/exam_export/pdf_service.py`
  - `src/backend/app/modules/exam_export/docx_service.py`

## Para que se hizo
- Corregir que ecuaciones y valores numéricos inline (ej. "80", "37°") aparecieran debajo del texto en lugar de dentro de la misma línea.
- Corregir que tablas con celdas de solo `mathInline` aparecieran vacías.
- Corregir que tablas desbordaran el ancho de la columna en DOCX.
- Eliminar espacio excesivo entre párrafos.
- Mostrar etiqueta A/B/C/D en opciones que son imagen pura.
- Corregir opción que no se renderizaba por usar `$$` como delimitador LaTeX.

## Que problemas se presentaron
- Nodos `image` a nivel top del doc (no dentro de `paragraph`) caían al handler genérico y se renderizaban como miniaturas de 27pt en lugar de bloque.
- `_merge_inline_image_paragraphs` con umbral 160px capturaba también gráficas generadas por IA (1400x900px pasadas por matplotlib) que tenían ih < 160 — se resolvió porque esas imágenes tienen ih >> 160.
- `OxmlElement("a:ln")` usaba el registro de namespaces de python-docx que no incluía el URI correcto de drawingml — se corrigió usando `lxml.etree.SubElement` con el namespace completo.
- El recuadro visible en imágenes inline resultó ser un artefacto visual de LibreOffice Writer (marco de objeto embebido), no un borde real en el archivo. En impresión y en Word no aparece.
- `_table_as_paragraph_matrix` llamaba a `_build_inline_markup` que aún no estaba definida en ese punto del archivo — no genera error en runtime pero es dependencia de orden de definición a tener en cuenta.

## Como se resolvieron
- Nodos `image` top-level: se agregó un `if node_type == "image"` explícito antes del handler de `paragraph` en `_render_tiptap_doc` y en `_render_tiptap_to_docx`.
- Doble dólar: `while clean.startswith("$") and clean.endswith("$")` en lugar de `if`.
- Namespaces DOCX: se usó `lxml.etree.SubElement` con URI completo `http://schemas.openxmlformats.org/drawingml/2006/main`.
- Anchos de tabla DOCX: se fijaron `w:tblW` y `w:tcW` explícitamente en twips calculados desde `column_width_in`.

## Que continua
- Exponer botones de exportación PDF y DOCX desde el frontend web en la sección de armado de examen.
- Evaluar caché de ecuaciones LaTeX (actualmente se regeneran por request).
- Validar comportamiento con ítems que mezclan imagen + ecuación + tabla en el mismo párrafo.
- Ajustar tamaño de imágenes inline en tablas si se requiere mayor legibilidad.

*(Archivos clave: `src/backend/app/modules/exam_export/pdf_service.py`, `src/backend/app/modules/exam_export/docx_service.py`)*
