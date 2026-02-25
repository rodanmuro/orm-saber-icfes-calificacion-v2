# Bitacora 021_02_24_2026 19:10:41 diseno_plantilla_v2_y_esquema

## Que fue lo que se hizo
- Se definio y ajusto iterativamente el wireframe de la nueva plantilla con ArUco + bloques funcionales:
  - Header para escritura manual.
  - Recuadro OMR de tipo de documento.
  - Recuadro OMR de numero de identidad del estudiante.
  - Recuadro OMR de identificacion de examen.
  - Recuadro inferior de respuestas.
- Se implemento/ajusto el script de prototipado para renderizar el wireframe sin afectar la plantilla vigente:
  - `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`.
- Se aplicaron ajustes de layout solicitados durante la sesion:
  - Recuadros superiores con expansiones controladas.
  - Gaps horizontales/verticales.
  - Header con distribucion de campos manuscritos.
  - Texto interno de burbujas en gris para reducir ruido visual al OMR.
  - Rotulos finales: `DOCUMENTO`, `NUMERO DE IDENTIDAD`, `IDENTIFICACION EXAMEN`.
- Se extendio el esquema de templates para soportar bloques auxiliares no presentes en v1:
  - `auxiliary_blocks` en config/layout.
  - Nuevos contratos para bloques auxiliares OMR/handwrite.
  - Validacion de bloques auxiliares dentro del area imprimible.
  - Archivos modificados:
    - `src/backend/app/modules/template_generator/contracts.py`
    - `src/backend/app/modules/template_generator/layout_engine.py`
- Se creo una configuracion nueva de plantilla oficial v2:
  - `src/backend/config/template.basica_omr_v2.json`.
- Se generaron artefactos v2 sin tocar v1:
  - `src/backend/data/output/template_basica_omr_v2.pdf`
  - `src/backend/data/output/template_basica_omr_v2.json`
- Se confirmo convivencia de versiones:
  - `src/backend/data/output/template_basica_omr_v1.json` permanece intacta.

## Para que se hizo
- Definir una plantilla v2 mas cercana al flujo real del proyecto (identificacion por OMR + zona de respuestas), manteniendo trazabilidad y sin romper el flujo existente en produccion/pruebas sobre v1.
- Preparar la base contractual para que el lector pueda evolucionar a lectura de bloques auxiliares (tipo de documento e identificadores), ademas de respuestas.

## Que problemas se presentaron
- Ajustes geometricos de recuadros superiores: inicialmente una expansion de ancho no estaba invadiendo el interior derecho como se esperaba.
- Distribucion de textos/lineas del header: algunas lineas de escritura quedaban visualmente altas.
- Restricciones de espacio horizontal: al agregar un tercer recuadro superior fue necesario reequilibrar anchos y gaps para mantener coherencia de lectura y diseno.

## Como se resolvieron
- Se corrigio la formula del recuadro derecho para que la expansion fuera real respecto a la linea interior del ArUco.
- Se recalibraron posiciones de baseline y lineas en el header para que las guias de escritura quedaran al pie de las etiquetas.
- Se reestructuro la fila superior a tres recuadros con gaps de 5 mm y reduccion del bloque de examen en columnas OMR, conservando legibilidad y consistencia visual.
- Se formalizo la solucion en schema/config v2 (no solo en wireframe), asegurando que el metadata exportado pueda ser consumido luego por el lector.

## Que continua
- Implementar lectura OMR de `auxiliary_blocks` en backend (documento, numero de identidad, identificacion de examen), manteniendo compatibilidad total con v1.
- Definir el contrato de salida para identidad/examen (valor leido, ambiguedad, columnas faltantes, bandera de revision manual).
- Preparar pruebas de integracion con plantilla fisica v2 y validar tolerancia a variaciones de luz/perspectiva.

*(Referencias clave: `src/backend/app/modules/template_generator/scripts/generate_layout_wireframe.py`, `src/backend/config/template.basica_omr_v2.json`, `src/backend/data/output/template_basica_omr_v2.json`.)*
