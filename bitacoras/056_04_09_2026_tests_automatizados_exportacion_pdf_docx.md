# Bitacora 056_04_09_2026 18:18:11 tests_automatizados_exportacion_pdf_docx

## Que fue lo que se hizo
- Se creó `src/backend/tests/test_exam_export_api.py` con 6 tests automatizados para los endpoints de exportación:
  - `test_export_pdf_texto_plano`: crea 2 ítems con texto plano, publica versión, llama `/export/pdf` y verifica status 200, content-type `application/pdf`, magic bytes `%PDF` y tamaño > 1 KB.
  - `test_export_pdf_con_math_inline`: ítem con doc Tiptap que contiene `mathInline` (LaTeX `x^2 + 1 = 0`), verifica que el render no explote y devuelva PDF válido.
  - `test_export_pdf_version_inexistente`: IDs inexistentes devuelven 404.
  - `test_export_docx_texto_plano`: mismo flujo para `/export/docx`, verifica magic bytes `PK` (ZIP/DOCX).
  - `test_export_docx_con_math_inline`: ítem con `mathInline` en enunciado y opciones como Tiptap JSON.
  - `test_export_docx_version_inexistente`: IDs inexistentes devuelven 404.
- Se usó SQLite en memoria (`tmp_path`) para no depender del servidor Postgres en CI.
- Se agregaron helpers `_tiptap_text` y `_tiptap_math_inline` para construir docs Tiptap JSON en los tests.
- Se agregó helper `_setup` que crea engine SQLite, override de `get_db` y teacher de prueba.
- Se agregó helper `_publish_version` que crea ítems, examen, los vincula y publica versión.

## Para que se hizo
- Formalizar como tests automatizados las pruebas manuales con `curl` que se venían haciendo durante el desarrollo de los servicios de exportación PDF y DOCX.
- Garantizar que futuros cambios en `pdf_service.py` o `docx_service.py` no rompan silenciosamente la exportación.

## Que problemas se presentaron
- Ninguno. Los 6 tests pasaron en la primera ejecución en 2.99 segundos.

## Como se resolvieron
- N/A

## Comandos curl para pruebas manuales

Listar exámenes y versiones para obtener los IDs:

```bash
curl -s http://localhost:8000/api/v1/exams | jq '[.[] | {id, title}]'
curl -s http://localhost:8000/api/v1/exams/{exam_id}/versions | jq '[.[] | {id, version_code}]'
```

Exportar con los IDs reales (ejemplo: exam_id=6, version_id=5):

```bash
curl -o examen.pdf "http://localhost:8000/api/v1/exams/6/versions/5/export/pdf"
curl -o examen.docx "http://localhost:8000/api/v1/exams/6/versions/5/export/docx"
```

Los archivos se crean en el directorio donde se ejecute el comando.

## Que continua
- Exponer botones de exportación PDF y DOCX desde el frontend web en la sección de armado de examen.
- Evaluar caché de ecuaciones LaTeX (actualmente se regeneran por request).
- Agregar test que cubra ítem con imagen adjunta (nodo `image` en Tiptap).
- Agregar test que cubra ítem con tabla (`table` en Tiptap).

*(Archivos clave: `src/backend/tests/test_exam_export_api.py`)*
