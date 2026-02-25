# HU_004 - Evolucion de plantilla OMR v2 con bloques auxiliares (EP_000)

## Trazabilidad
- Epica asociada: `EP_000_generador_plantilla_basica_omr_con_aruco.md`
- Complementa HU_01..HU_06 con una version evolucionada de plantilla sin romper `v1`.

## Historia de usuario
**Como** equipo tecnico del generador de plantillas  
**Quiero** una plantilla `v2` con bloques auxiliares (header, tipo de documento, numero de identidad, identificacion de examen) ademas del bloque de respuestas  
**Para** soportar identificacion OMR del estudiante/examen y mejorar el diseno operativo de captura.

## Criterios de aceptacion
1. Existe configuracion de plantilla v2 separada de v1.
2. Se genera metadata `template_basica_omr_v2.json` sin alterar ni reemplazar `template_basica_omr_v1.json`.
3. El esquema de template soporta `auxiliary_blocks` para bloques no-respuesta.
4. Se conserva compatibilidad del generador para configuraciones anteriores (v1).
5. Se dispone de PDF wireframe para iteracion visual de layout v2.

## Evidencia esperada
- Configuracion v2:
  - `src/backend/config/template.basica_omr_v2.json`
- Artefactos generados:
  - `src/backend/data/output/template_basica_omr_v2.json`
  - `src/backend/data/output/template_basica_omr_v2.pdf`
- Soporte de esquema/layout:
  - `src/backend/app/modules/template_generator/contracts.py`
  - `src/backend/app/modules/template_generator/layout_engine.py`
- Wireframe de iteracion:
  - `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`

## Notas
- Esta HU cubre diseno y estructura de plantilla; la lectura de bloques auxiliares en backend lector se planifica en actividades de EP_001.
