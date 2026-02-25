# Bitacora 023_02_24_2026 21:13:23 ruta_unica_render_plantilla_v2

## Que fue lo que se hizo
- Se consolidó el diagnostico del problema de plantilla v2: se estaban mezclando dos rutas de generacion diferentes para el PDF.
- Se confirmo que la ruta de `generate_template` (renderer base) no replica de forma fiel el layout visual que ya fue validado en campo para v2.
- Se restauraron cambios experimentales del renderer base para evitar degradaciones visuales no controladas.
- Se regenero `src/backend/data/output/template_basica_omr_v2.pdf` usando la ruta de wireframe, que corresponde al layout oficial validado.
- Se dejo documentado el comando operativo unico para renderizar v2:
  - `python -m app.modules.template_generator.scripts.generate_layout_wireframe --config config/template.basica_omr_v2.json --output data/output/template_basica_omr_v2.pdf`

## Para que se hizo
- Evitar inconsistencias de plantilla entre lo que se diseña y lo que realmente se imprime en produccion.
- Estabilizar el flujo de trabajo para que todo el equipo use una sola ruta de renderizado para v2.
- Reducir riesgo de errores de lectura OMR causados por cambios visuales involuntarios en la plantilla.

## Que problemas se presentaron
- El PDF de `template_basica_omr_v2` quedo incompleto o desalineado en diferentes iteraciones.
- Aparecieron diferencias de layout (header, bloques auxiliares y bloque de respuestas) por usar pipelines distintos.
- Se intento corregir sobre el renderer base, pero ese camino altero salidas y genero confusion frente al artefacto oficial ya impreso.

## Como se resolvieron
- Se identifico como causa raiz la mezcla entre:
  - `app.modules.template_generator.scripts.generate_template`
  - `app.modules.template_generator.scripts.generate_layout_wireframe`
- Se retiro la modificacion experimental de `src/backend/app/modules/template_generator/template_renderer.py` para volver a un estado estable.
- Se regenero el artefacto v2 oficial con la ruta wireframe y config v2 actual.
- Se acordo operativamente que, hasta unificar definitivamente arquitectura de render, la plantilla v2 oficial se genera solo por wireframe.

## Que continua
- Formalizar en documentacion tecnica (README backend y/o metodologia) que v2 usa ruta unica temporal de wireframe.
- Evaluar una consolidacion posterior para que exista un solo renderer definitivo y se elimine duplicidad de pipelines.
- Continuar con la configuracion y validacion del lector OMR de la nueva plantilla v2 usando fotos reales.

*(Archivos clave relacionados: `src/backend/config/template.basica_omr_v2.json`, `src/backend/data/output/template_basica_omr_v2.pdf`, `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`, `src/backend/app/modules/template_generator/template_renderer.py`.)*
