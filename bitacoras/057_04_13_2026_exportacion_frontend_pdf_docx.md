# Bitacora 057_04_13_2026 08:28:12 exportacion_frontend_pdf_docx

## Que fue lo que se hizo
- Se actualizo la planeacion para alinear lo implementado en exportacion de examenes por version:
  - `planeacion/00_epicas/EP_002_banco_items_y_generacion_examenes_web.md`
  - `planeacion/01_historias_de_usuario/HU_016_EP_002_exportacion_examen_imprimible_pdf.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0064_HU_16_EP_002_TODO.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0065_HU_16_EP_002_TODO.md`
- Se integro en frontend (pestana Armado de examen) la exportacion directa por examen usando la ultima version publicada:
  - `Exportar a PDF`
  - `Exportar a DOCX`
- Se agregaron funciones de API frontend para descarga de binarios:
  - `src/frontend_web/src/api/examsApi.js`
- Se incorporaron handlers de exportacion y ventana de loading durante el proceso de descarga/exportacion:
  - `src/frontend_web/src/App.jsx`
- Se ajusto la tabla `Examenes del docente` para mejorar UX:
  - Separacion de columna `Accion` (solo abrir) y columna `Exportar` (PDF/DOCX).
  - Distribucion visual de botones para evitar amontonamiento.
  - `src/frontend_web/src/components/ExamBuilder.jsx`
  - `src/frontend_web/src/styles.css`
- Se valido compilacion de frontend con `npm run build` en verde.

## Para que se hizo
- Cerrar la brecha entre backend (endpoints de exportacion ya disponibles) y frontend (sin acciones de descarga).
- Permitir al docente exportar rapidamente cuadernillos desde la interfaz sin usar comandos `curl`.
- Mejorar usabilidad de la tabla de examenes para que las acciones de apertura y exportacion queden claras y separadas.
- Dejar la documentacion de planeacion coherente con lo que ya se ejecuto en codigo.

## Que problemas se presentaron
- Se introdujo inicialmente un boton de `Exportar a Excel` por confusion de alcance, pero el requerimiento real era `PDF + DOCX`.
- Los botones de accion y exportacion quedaron visualmente amontonados en la misma columna.
- Existia desalineacion entre el estado real del desarrollo y archivos de planeacion (HU/ACT/EP).

## Como se resolvieron
- Se retiro la logica de exportacion CSV/Excel y se reemplazo por exportacion DOCX real usando el endpoint backend existente.
- Se separo la tabla en dos columnas (`Accion` y `Exportar`) y se aplicaron estilos especificos:
  - contenedor `export-actions`
  - anchos minimos para evitar colision de botones
- Se actualizaron HU/ACT/EP para reflejar exactamente el alcance actual: exportacion por version en PDF y DOCX.
- Se agrego overlay de loading y estado de boton (`Generando...`) para feedback claro durante exportacion.

## Que continua
- Conectar botones de exportacion por fila de version publicada (ademas del esquema por ultima version) para control explicito del docente.
- Agregar pruebas frontend (o E2E) para flujo de exportacion PDF/DOCX desde `Armado de examen`.
- Crear bitacora de cierre cuando se confirme validacion manual completa de UX de exportacion.

*(Archivos clave: `src/frontend_web/src/App.jsx`, `src/frontend_web/src/components/ExamBuilder.jsx`, `src/frontend_web/src/api/examsApi.js`, `planeacion/01_historias_de_usuario/HU_016_EP_002_exportacion_examen_imprimible_pdf.md`)*
