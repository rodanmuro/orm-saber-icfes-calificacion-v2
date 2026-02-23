# Bitacora 016_02_23_2026 17:42:55 pruebas_omr_con_ajuste_umbral_y_regla_mayor_ratio_con_deuda_tecnica

## Que fue lo que se hizo
- Se ajusto el umbral de marcado a `0.12` para el flujo backend/frontend:
  - `src/backend/app/api/v1/endpoints/omr_read.py`
  - `src/backend/app/modules/omr_reader/api_service.py`
  - `src/frontend/src/services/omrRead.js`
- Se implemento regla de resolucion por pregunta: si varias opciones superan umbral, queda marcada solo la de mayor ratio:
  - `src/backend/app/modules/omr_reader/result_builder.py`
  - `src/backend/tests/test_omr_result_builder.py`
- Se ejecutaron pruebas de regresion de backend:
  - `src/backend/tests/test_omr_result_builder.py`
  - `src/backend/tests/test_omr_api_service.py`
- Se corrio un barrido sobre imagenes reales en `src/backend/data/input/mobile_uploads` para medir exactitud por archivo.
- Se generaron artefactos de depuracion (imagen alineada, binaria y CSV de ratios) para casos especificos:
  - `mobile_20260223_153237_e2b2c4cf`
  - `mobile_20260223_151802_9cd3b64b`
  - `mobile_20260223_151511_6db722dc`
  - `mobile_20260223_142842_c7da6c72`

## Para que se hizo
- Incrementar sensibilidad en marcas tenues reales sin perder control del resultado por pregunta.
- Evitar respuesta multiple final por pregunta cuando varias opciones superan umbral.
- Medir el comportamiento real del sistema con fotos de celular en lote, no solo con pruebas unitarias.
- Construir trazabilidad visual y numerica para analizar fallos concretos.
- Nota de calibracion: el valor `0.12` se definio de forma empirica (por tanteo), a partir de visualizacion de ratios observados en varias imagenes reales, y no aun por un proceso formal de optimizacion estadistica.

## Que problemas se presentaron
- Persisten casos limite con variabilidad de iluminacion y reflejos donde algunas marcas quedan por debajo del umbral.
- Existe un caso de fallo por deteccion ArUco incompleta (`id=0` no detectado) en una imagen.
- Con umbrales bajos existe riesgo funcional:
  - que el estudiante marque varias opciones y el sistema seleccione solo una (la mayor), ocultando la invalidez de la pregunta.
  - que una marca espuria pequena (punto/trazo leve) sea interpretada como opcion valida.

## Como se resolvieron
- Se adopto temporalmente `marked_threshold=0.12` como calibracion operativa por tanteo, guiada por inspeccion visual de ratios en casos reales.
- Se aplico regla determinista de desempate por mayor ratio para entregar una sola opcion por pregunta.
- Se verifico en imagenes reales principales:
  - `153237`: 30/30
  - `151802`: 30/30
- Se dejaron artefactos debug para inspeccion manual de casos de baja exactitud (por ejemplo `151511` y `142842`) y poder tomar decisiones de siguiente iteracion.

## Que continua
- Deuda tecnica 1: cuando haya multiples marcas reales del estudiante, no debe consolidarse automaticamente a una sola; debe marcarse como invalida para calificacion.
- Deuda tecnica 2: incorporar una regla anti-marca-espuria (punto leve), por ejemplo con umbral relativo por pregunta y margen minimo sobre segunda opcion.
- Deuda tecnica 3: definir politica de “sin respuesta” robusta para trazos muy tenues y condiciones de baja iluminacion.
- Deuda tecnica 4: formalizar pruebas de aceptacion por lote con reporte versionado (exactitud, falsos positivos, falsos negativos, casos ArUco fallidos).
- Deuda tecnica 5 (frontend futuro): ante alertas de ambiguedad o marca espuria, construir un dashboard de correccion manual que permita revisar la imagen procesada y confirmar/editar la opcion por pregunta antes de cerrar la calificacion.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
