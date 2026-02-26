# Bitacora 026_02_26_2026 08:28:12 arquitecura_pipeline_plantilla_v2_deuda_tecnica

## Que fue lo que se hizo
- Se consolido la documentacion de la arquitectura vigente de plantilla v2 en una bitacora dedicada, evitando dejar el contenido como documento suelto sin trazabilidad temporal.
- Se dejo explicito el pipeline tecnico actual con los archivos involucrados:
  - Config base: `src/backend/config/template.basica_omr_v2.json`
  - Compilacion de metadata runtime: `src/backend/app/modules/template_generator/scripts/generate_wireframe_metadata.py`
  - Metadata operativo: `src/backend/data/output/template_basica_omr_v2_wireframe.json`
  - Render PDF desde metadata: `src/backend/app/modules/template_generator/scripts/generate_pdf_from_metadata.py`
  - Consumo en lectura OMR: `src/backend/app/api/v1/endpoints/omr_read.py` y `src/backend/app/core/config.py`
- Se registro la decision vigente: la geometria runtime la define el wireframe metadata compilado, no directamente el JSON base de configuracion.
- Se actualizo `README.md` para referenciar esta bitacora como fuente de contexto arquitectonico actual.
- Se retiro el archivo suelto `planeacion/arquitectura_pipeline_plantilla_v2.md` para no duplicar el mismo contenido en dos ubicaciones.

## Para que se hizo
- Mantener consistencia documental con la metodologia del proyecto basada en bitacoras con consecutivo.
- Dejar clara la arquitectura actual antes de futuras mejoras hacia plantillas customizables.
- Evitar confusiones sobre cual JSON es de configuracion y cual JSON es de operacion runtime.

## Que problemas se presentaron
- Habia ambiguedad de interpretacion por coexistencia de dos JSON con roles distintos.
- El documento de arquitectura quedaba como archivo aislado fuera del flujo cronologico de decisiones.
- Riesgo de asumir incorrectamente que `template.basica_omr_v2.json` se consume de forma directa en runtime.

## Como se resolvieron
- Se documento el pipeline end-to-end en esta bitacora, con rutas concretas y responsabilidades por archivo/script.
- Se formalizo la decision actual de arquitectura:
  - `template.basica_omr_v2.json` = configuracion base editable.
  - `template_basica_omr_v2_wireframe.json` = metadata operativo runtime para render y lectura.
- Se alineo la referencia de documentacion en `README.md` para apuntar a la bitacora de decision tecnica.

## Que continua
- Ejecutar `ACT_0031_HU_07_EP_000_TODO.md` para definir si el sistema evoluciona a fuente unica de verdad o mantiene compilacion formalizada con contrato claro.
- Definir validaciones automaticas de coherencia entre config base, metadata runtime y PDF generado.
- Preparar soporte de plantillas customizables con reglas de versionado y migracion de metadata.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
