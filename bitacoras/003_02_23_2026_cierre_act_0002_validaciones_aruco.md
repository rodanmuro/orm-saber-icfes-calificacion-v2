# Bitacora 003_02_23_2026 08:38:29 cierre_act_0002_validaciones_aruco

## Que fue lo que se hizo
- Se implemento y cerro `ACT_0002` enfocada en integracion ArUco configurable y validada.
- Se extendio la configuracion ArUco para soportar offsets por esquina (`corner_offsets_mm`) y validaciones de diccionario/IDs:
  - `src/backend/app/modules/template_generator/contracts.py`
- Se actualizo el posicionamiento de ArUco para calcularse con base en el area imprimible (no solo por borde de pagina):
  - `src/backend/app/modules/template_generator/aruco_renderer.py`
- Se agregaron reglas de validacion en layout para:
  - marcadores fuera del area imprimible,
  - colision de marcadores con bloque principal.
  - Archivo: `src/backend/app/modules/template_generator/layout_engine.py`
- Se ampliaron utilidades geometricas para representar cuadrados desde centro y detectar solapamientos rectangulares:
  - `src/backend/app/modules/template_generator/geometry.py`
- Se actualizo configuracion base con `corner_offsets_mm`:
  - `src/backend/config/template.base.json`
- Se regeneraron artefactos de salida:
  - `src/backend/output/template_basica_omr_v1.json`
  - `src/backend/output/template_basica_omr_v1.pdf` (ignorado por git)
- Se agregaron y ajustaron pruebas automaticas para cubrir los nuevos casos:
  - `src/backend/tests/test_aruco_renderer.py`
  - `src/backend/tests/test_contracts.py`
  - `src/backend/tests/test_layout_engine.py`
- Se actualizo estado de actividad:
  - `planeacion/02_actividades/epicas/EP_000_generador_plantilla_basica_omr_con_aruco/ACT_0002_HU_02_EP_000_DONE.md`
  - Eliminado `planeacion/02_actividades/epicas/EP_000_generador_plantilla_basica_omr_con_aruco/ACT_0002_HU_02_EP_000_TODO.md`

## Para que se hizo
- Garantizar que la ubicacion de ArUco sea realmente parametrizable por configuracion y segura respecto al area imprimible.
- Evitar layouts invalidos por marcadores fuera de limites o superpuestos con el bloque de lectura.
- Dejar evidencia automatica de calidad para cambios futuros en el motor de plantillas.

## Que problemas se presentaron
- Se presento un error inicial por definicion de clases de offsets anidadas en contratos, que rompia validacion en tiempo de carga.
- Tras corregirlo, algunos tests fallaron porque los offsets no tenian defaults explicitos en ausencia de configuracion.

## Como se resolvieron
- Se movieron DTOs de offsets a nivel de modulo y se corrigio el modelado de `ArucoConfig`.
- Se definieron defaults `0.0` para `x_mm` y `y_mm` en offsets, manteniendo compatibilidad con configuraciones previas.
- Se reejecuto la suite completa y se confirmo estado verde.

## Que continua
- Iniciar `ACT_0003` para consolidar el bloque rectangular principal como componente parametrizable desacoplado.
- Mantener ciclo de implementacion incremental con pruebas automaticas por actividad.
- Evaluar en `ACT_0004` la incorporacion de etiquetas visuales A/B/C/D dentro de burbujas como capacidad configurable.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
