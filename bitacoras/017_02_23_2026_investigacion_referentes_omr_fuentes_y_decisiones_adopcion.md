# Bitacora 017_02_23_2026 19:22:51 investigacion_referentes_omr_fuentes_y_decisiones_adopcion

## Que fue lo que se hizo
- Se realizo una revision investigativa de referentes OMR externos, enfocada en flujo de lectura de imagen y robustez en capturas reales de celular.
- Se inspeccionaron y analizaron:
  - `https://github.com/EuracBiomedicalResearch/RescueOMR`
  - `https://github.com/gramcracker40/LiveTest`
  - `https://github.com/gramcracker40/LiveTest/blob/master/LiveTestFilePaper.pdf`
- Se reviso el backend de LiveTest en entorno local clonado para entender su pipeline de preprocesamiento y lectura.
- Se discutieron decisiones de arquitectura para nuestro proyecto, manteniendo el alcance actual en investigacion (sin agregar implementaciones nuevas derivadas de este analisis).

## Para que se hizo
- Identificar tecnicas de preprocesamiento y criterios de robustez que puedan mejorar lectura en imagenes reales.
- Evitar adoptar patrones no alineados con nuestro enfoque (ArUco obligatorio 4/4).
- Definir, con criterio tecnico, que ideas se incorporan como tareas futuras y cuales se descartan por ahora.

## Que problemas se presentaron
- Riesgo de desviarse del enfoque investigativo e implementar cambios prematuros sin cerrar primero decisiones.
- Diferencias de contexto entre proyectos de referencia:
  - repos orientados a escaneo/lote documental vs nuestro caso de captura movil.
  - supuestos de calidad de marcado (burbujas bien rellenas) que no siempre se cumplen en pruebas reales.
- En las referencias no siempre hay reporte estandarizado de metricas comparables (accuracy end-to-end en el mismo formato que necesitamos).

## Como se resolvieron
- Se acordaron criterios de adopcion estrictos:
  - mantener `ArUco 4/4` obligatorio (sin fallback por contornos).
  - priorizar mejoras de preprocesamiento y metricas de confianza antes de calificacion final.
- Se consolidaron como direccion de trabajo (para implementar despues):
  - variante adicional en `robust_mode`: `CLAHE -> GaussianBlur(5x5) -> OTSU_INV`.
  - seleccion de variante por metricas: menos ambiguas + mayor separacion `top1-top2`.
  - señal opcional de confianza (diagnostica) y descarte si aumenta demasiado la latencia.
- Se documento que el umbral `0.12` actual fue calibrado empiricamente por tanteo/visualizacion en imagenes reales (no optimizacion estadistica formal).

## Que continua
- Formalizar actividades nuevas de investigacion aplicada (sin mezclar aun con implementacion productiva):
  - benchmark reproducible por lote con metricas uniformes.
  - protocolo de captura movil (luz, angulo, distancia, marcadores visibles).
  - evaluacion de variantes de preproceso y costo computacional.
- Convertir decisiones adoptadas en tareas tecnicas concretas dentro de la planeacion de EP_001.
- Mantener deuda tecnica visible:
  - multiple marca real del estudiante,
  - marca espuria (puntos/trazos leves),
  - dashboard futuro de revision/correccion manual.
- Enlace operativo ya creado para continuidad:
  - HU nueva: `planeacion/01_historias_de_usuario/HU_002_EP_001_mejoras_robustez_lectura_omr.md`
  - Actividades nuevas:
    - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0017_HU_10_EP_001_TODO.md`
    - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0018_HU_10_EP_001_TODO.md`
    - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0019_HU_11_EP_001_TODO.md`
    - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0020_HU_11_EP_001_TODO.md`
    - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0021_HU_12_EP_001_TODO.md`

## Fuentes consultadas
- RescueOMR:
  - `https://github.com/EuracBiomedicalResearch/RescueOMR`
- LiveTest:
  - `https://github.com/gramcracker40/LiveTest`
  - `https://github.com/gramcracker40/LiveTest/blob/master/LiveTestFilePaper.pdf`
- Seccion revisada en LiveTest backend:
  - `backend/answer_sheets/grader.py`
  - `backend/answer_sheets/main.py`

## Con que nos quedamos para nuestro proyecto
- Si adoptamos:
  - fortalecimiento de preprocesamiento por variantes.
  - criterio cuantitativo de confianza por pregunta (margen entre mejores opciones).
  - trazabilidad visual por etapa para depuracion.
- No adoptamos por ahora:
  - fallback de alineacion sin ArUco.
  - cambio de mapeo de preguntas basado solo en agrupacion heuristica de contornos.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
