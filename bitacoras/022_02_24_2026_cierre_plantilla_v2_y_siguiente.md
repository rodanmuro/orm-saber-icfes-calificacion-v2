# Bitacora 022_02_24_2026 19:19:50 cierre_plantilla_v2_y_siguiente

## Que fue lo que se hizo
- Se consolidó el diseño de la plantilla v2 con wireframe funcional y ajustes geométricos en:
  - `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`
  - `src/backend/data/output/template_wireframe_layout_v1.pdf`
- Se formalizó la v2 en el esquema del generador, agregando soporte para bloques auxiliares (`auxiliary_blocks`) en:
  - `src/backend/app/modules/template_generator/contracts.py`
  - `src/backend/app/modules/template_generator/layout_engine.py`
- Se creó la configuración oficial de plantilla v2:
  - `src/backend/config/template.basica_omr_v2.json`
- Se generaron artefactos de salida v2:
  - `src/backend/data/output/template_basica_omr_v2.json`
  - `src/backend/data/output/template_basica_omr_v2.pdf`
- Se mantuvo convivencia explícita con v1 (sin reemplazar):
  - `src/backend/data/output/template_basica_omr_v1.json`
- Se actualizó planeación/actividades:
  - Cierre de ACT_0013, ACT_0014, ACT_0015 y ACT_0023 en estado DONE.
  - Creación de HU nueva de evolución de plantilla v2 y ACT asociadas (`ACT_0027`, `ACT_0028`, `ACT_0029`).

## Para que se hizo
- Dejar estable una plantilla v2 con estructura real de operación (header, documento, identidad, examen y respuestas), sin afectar el flujo activo basado en v1.
- Preparar la base contractual para el siguiente paso: lectura OMR de bloques auxiliares en backend.

## Que problemas se presentaron
- Durante el ajuste de wireframe hubo diferencias entre “llegar a borde interior ArUco” y “invadirlo” en el recuadro de identificación de examen.
- Se detectó necesidad de reequilibrar anchos/gaps al introducir el recuadro adicional de tipo de documento.
- Algunas etiquetas y líneas del header no quedaban visualmente alineadas en primera iteración.

## Como se resolvieron
- Se ajustaron fórmulas geométricas del script wireframe para asegurar expansiones exactas y verificables.
- Se validaron posiciones con cálculos numéricos de límites internos ArUco antes de regenerar PDF.
- Se refinó distribución del header y estilo de texto en burbujas (gris claro) para disminuir riesgo de lectura espuria.

## Que continua
- Configurar el lector OMR para `template_basica_omr_v2.json` y leer bloques auxiliares además de respuestas:
  - `DOCUMENTO` (selección única).
  - `NUMERO DE IDENTIDAD` (10x12, una marca por columna).
  - `IDENTIFICACION EXAMEN` (10x4, una marca por columna).
- Definir salida estructurada v2 con trazabilidad y flags de revisión manual por ambigüedad/ausencia de marca.
- Mantener compatibilidad total hacia atrás con `template_basica_omr_v1.json`.

*(Referencias: `bitacoras/021_02_24_2026_diseno_plantilla_v2_y_esquema.md`, `planeacion/01_historias_de_usuario/HU_004_EP_000_evolucion_plantilla_omr_v2_con_bloques_auxiliares.md`.)*
