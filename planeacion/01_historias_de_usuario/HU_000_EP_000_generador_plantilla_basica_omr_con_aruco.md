# HU_000 - Historias de Usuario de EP_000 (Generador de plantilla basica OMR con ArUco)

## Trazabilidad
- Epica asociada: `EP_000_generador_plantilla_basica_omr_con_aruco.md`
- Objetivo de la epica: generar una plantilla basica OMR en formato carta con 4 ArUco y metadatos geometricos consumibles por el modulo de lectura.

## HU_01 - Definir layout base de pagina carta
**Como** equipo de desarrollo  
**Quiero** definir una geometria base de pagina carta con margenes y areas reservadas  
**Para** garantizar consistencia y repetibilidad del layout generado.

### Criterios de aceptacion
1. El generador usa una configuracion explicita de tamano carta.
2. Los margenes de trabajo quedan definidos en parametros del generador.
3. La plantilla resultante mantiene la misma geometria en ejecuciones consecutivas con la misma configuracion.

### Evidencia esperada
- Modulo/configuracion de layout en `src/`.
- Plantilla generada en artefacto de salida (PDF o imagen).

---

## HU_02 - Ubicar 4 marcadores ArUco en esquinas logicas
**Como** motor de alineacion OMR  
**Quiero** que la plantilla incluya 4 ArUco en esquinas logicas con margen seguro  
**Para** poder corregir perspectiva en captura movil.

### Criterios de aceptacion
1. La plantilla incluye exactamente 4 ArUco.
2. Cada ArUco se ubica en una esquina logica distinta (superior-izquierda, superior-derecha, inferior-izquierda, inferior-derecha).
3. Ningun ArUco queda fuera del area imprimible definida por margenes.

### Evidencia esperada
- Salida visual con 4 ArUco visibles.
- Coordenadas de los ArUco en archivo de metadatos de plantilla.

---

## HU_03 - Incluir bloque rectangular principal de lectura
**Como** modulo OMR  
**Quiero** un bloque rectangular principal dentro de la pagina  
**Para** delimitar la region util donde se ubican las burbujas.

### Criterios de aceptacion
1. El bloque rectangular principal es visible en la plantilla.
2. El bloque se define por coordenadas parametrizadas.
3. El bloque no colisiona geometricamente con los ArUco.

### Evidencia esperada
- Plantilla visual con bloque rectangular identificable.
- Metadatos del bloque en archivo de plantilla.

---

## HU_04 - Generar conjunto inicial de burbujas OMR con IDs estables
**Como** modulo de lectura posterior  
**Quiero** una serie de burbujas OMR con identificadores estables  
**Para** mapear de forma deterministica cada burbuja al resultado de lectura.

### Criterios de aceptacion
1. El generador produce un conjunto inicial de burbujas dentro del bloque rectangular.
2. Cada burbuja tiene un ID unico y estable entre ejecuciones con misma configuracion.
3. Todas las burbujas definidas en metadatos aparecen visualmente en la plantilla.

### Evidencia esperada
- Plantilla visual con burbujas.
- Lista de burbujas con IDs y geometria en metadatos.

---

## HU_05 - Exportar metadatos geometricos de plantilla
**Como** consumidor del layout (lectura local)  
**Quiero** un archivo de metadatos estructurado (por ejemplo `template.json`)  
**Para** usar coordenadas sin inferencias manuales.

### Criterios de aceptacion
1. Se genera un archivo de metadatos junto con la plantilla visual.
2. El archivo contiene dimensiones de pagina, ArUco, bloque principal y burbujas.
3. Existe correspondencia 1:1 entre burbujas visibles y burbujas declaradas en metadatos.

### Evidencia esperada
- Archivo `template.json` (o equivalente) en salida.
- Validacion basica de estructura y campos obligatorios.

---

## HU_06 - Exponer comando reproducible de generacion
**Como** desarrollador del proyecto  
**Quiero** un comando/script unico para regenerar plantilla y metadatos  
**Para** asegurar reproducibilidad en desarrollo y sprint.

### Criterios de aceptacion
1. Existe un comando documentado para ejecutar el generador.
2. El comando produce siempre los dos artefactos esperados (plantilla visual y metadatos).
3. Si faltan parametros obligatorios, el comando falla con mensaje controlado.

### Evidencia esperada
- Entrada en documentacion tecnica con comando de generacion.
- Artefactos generados tras ejecucion del comando.

---

## Notas de implementacion para sprint
- Mantener IDs estables para trazabilidad (`HU_01` ... `HU_06`).
- Evitar incluir en esta HU funcionalidades fuera de alcance de `EP_000` (calificacion, API, OCR, captura en tiempo real).
- El detalle operativo de tareas se define en actividades `ACT_XXXX` durante sprint planning.
