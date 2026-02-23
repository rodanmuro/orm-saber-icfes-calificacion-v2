# Bitacora 008_02_23_2026 10:31:33 inicio_ep_001_y_rutas_data

## Que fue lo que se hizo
- Se inicio formalmente la epica `EP_001` orientada a lectura OMR desde fotos (alcance limitado, sin movil por ahora).
- Se crearon historias de usuario de `EP_001` con criterios verificables:
  - `planeacion/01_historias_de_usuario/HU_001_EP_001_lectura_movil_local_omr_a_json.md`
- Se crearon actividades tecnicas `TODO` de `EP_001`:
  - `ACT_0007_HU_01_EP_001_TODO.md`
  - `ACT_0008_HU_02_EP_001_TODO.md`
  - `ACT_0009_HU_03_EP_001_TODO.md`
  - `ACT_0010_HU_04_EP_001_TODO.md`
  - `ACT_0011_HU_05_EP_001_TODO.md`
  - `ACT_0012_HU_06_EP_001_TODO.md`
- Se implemento en codigo `ACT_0007` (carga local de imagen + metadata con validaciones y errores controlados):
  - `src/backend/app/modules/omr_reader/errors.py`
  - `src/backend/app/modules/omr_reader/contracts.py`
  - `src/backend/app/modules/omr_reader/loader.py`
  - `src/backend/app/modules/omr_reader/scripts/validate_read_input.py`
- Se actualizo `ACT_0007` a `DONE`:
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0007_HU_01_EP_001_DONE.md`
- Se estandarizaron rutas de datos a `src/backend/data/`:
  - carpeta de entradas: `src/backend/data/input/` (con `.gitkeep`)
  - carpeta de salidas: `src/backend/data/output/`
- Se ajustaron rutas en documentacion y reglas de ignore:
  - `.gitignore` (PDFs en `src/backend/data/output/*.pdf`, imagenes de prueba en `src/backend/data/input/*`)
  - `src/backend/README.md` (comandos con rutas `data/output`)

## Para que se hizo
- Preparar una base de lectura OMR local robusta para trabajar con fotos reales diligenciadas antes de integrar movil.
- Mejorar coherencia estructural del proyecto centralizando entradas/salidas en `data/`.
- Reducir riesgo de errores en pruebas locales con validaciones tempranas de insumos.

## Que problemas se presentaron
- Se detecto inconsistencia de rutas al coexistir `src/backend/output` y la nueva carpeta `data/output`.
- En una validacion manual hubo un error puntual de ruta al ejecutar un comando de prueba.

## Como se resolvieron
- Se movieron artefactos de salida a `src/backend/data/output` y se actualizaron referencias activas.
- Se ajusto `.gitignore` para mantener repositorio limpio con imagenes de prueba y PDFs generados.
- Se reejecutaron pruebas automaticas para validar que el cambio de rutas no rompio funcionalidades existentes.
- Resultado de pruebas: 28 tests aprobados.

## Que continua
- Avanzar con `ACT_0008` (deteccion ArUco + homografia) para alinear fotos al plano de plantilla.
- Agregar tests automaticos del modulo `omr_reader` creado en `ACT_0007`.
- Mantener trazabilidad de estados de actividades y evidencia tecnica por cada incremento.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
