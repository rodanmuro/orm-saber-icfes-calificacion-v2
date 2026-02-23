# HU_001 - Historias de Usuario de EP_001 (Lectura local OMR a JSON desde fotos)

## Trazabilidad
- Epica asociada: `EP_001_lectura_movil_local_omr_a_json.md`
- Alcance ajustado para esta fase: lectura desde fotos de plantillas diligenciadas (sin implementacion movil en esta etapa).

## HU_01 - Cargar imagen de prueba y metadatos de plantilla
**Como** modulo de lectura OMR  
**Quiero** cargar una foto de la plantilla y el JSON de metadatos generado por EP_000  
**Para** iniciar el pipeline de lectura sobre una base geometrica conocida.

### Criterios de aceptacion
1. El sistema recibe una ruta de imagen valida y un `template.json` valido.
2. Si falta la imagen o el `template.json`, retorna error controlado y legible.
3. Se valida que `template_id`/`version` existan en metadatos antes de procesar.

### Evidencia esperada
- Modulo de carga de imagen y metadata en `src/backend`.
- Caso de ejecucion local con archivo de foto real y metadata asociada.

---

## HU_02 - Detectar ArUco y corregir perspectiva en foto
**Como** motor de lectura  
**Quiero** detectar los 4 ArUco y aplicar correccion de perspectiva  
**Para** normalizar la imagen al plano de plantilla y poder evaluar burbujas con precision.

### Criterios de aceptacion
1. Con foto valida, el sistema detecta los 4 ArUco esperados.
2. Si faltan ArUco o no hay deteccion suficiente, retorna error controlado.
3. El resultado de homografia genera una imagen alineada al layout de plantilla.

### Evidencia esperada
- Funcion/modulo de deteccion ArUco + homografia.
- Salida intermedia de imagen corregida para inspeccion local.

---

## HU_03 - Evaluar estado de burbujas (marcada/no_marcada)
**Como** modulo OMR  
**Quiero** evaluar cada burbuja del layout corregido usando ROI y umbral documentado  
**Para** clasificar cada opcion como `marcada` o `no_marcada`.

### Criterios de aceptacion
1. Cada burbuja de `question_items` es evaluada exactamente una vez.
2. La clasificacion se basa en una regla reproducible (umbral/porcentaje de relleno).
3. El sistema detecta y reporta burbujas ambiguas cuando aplique (regla definida).

### Evidencia esperada
- Modulo de evaluacion de ROI por burbuja.
- Parametros de umbral documentados en configuracion/codigo.

---

## HU_04 - Generar JSON de resultados por pregunta
**Como** consumidor del resultado OMR  
**Quiero** un JSON estructurado por pregunta/opcion  
**Para** analizar respuestas leidas y su calidad sin dependencias externas.

### Criterios de aceptacion
1. El JSON contiene `template_id`, `version`, `timestamp` y resultados por pregunta.
2. Cada pregunta incluye opciones con estado (`marcada`/`no_marcada`).
3. El JSON incluye metadatos de calidad basicos (ej: confianza global o contador de ambiguas).

### Evidencia esperada
- Archivo JSON de salida generado localmente.
- Esquema/documento corto del formato de salida.

---

## HU_05 - Validar precision con set de fotos diligenciadas
**Como** equipo de desarrollo  
**Quiero** ejecutar pruebas con fotos reales de plantillas diligenciadas  
**Para** medir precision inicial del lector antes de pasar a integracion movil.

### Criterios de aceptacion
1. Existe un set minimo de fotos de prueba versionadas o referenciadas.
2. Se comparan resultados leidos vs verdad esperada para cada foto.
3. Se reporta una metrica de precision inicial (por burbuja y/o por pregunta).

### Evidencia esperada
- Script/comando de evaluacion sobre dataset de fotos.
- Reporte resumen de precision con resultados observables.

---

## HU_06 - CLI reproducible para ejecucion local completa
**Como** desarrollador  
**Quiero** un comando unico para ejecutar lectura en una foto y obtener salida JSON  
**Para** repetir pruebas y depurar sin interfaz movil.

### Criterios de aceptacion
1. Existe un comando CLI documentado para ejecutar fin a fin.
2. El comando valida argumentos requeridos y falla con errores controlados.
3. El mismo comando funciona con distintas fotos/configuraciones sin cambiar codigo.

### Evidencia esperada
- Script CLI en `src/backend`.
- Seccion de uso en `README` tecnico.

---

## Notas de alcance para sprint
- Esta HU_001 limita alcance a backend/local con fotos estaticas; no incluye app movil.
- No incluye scoring de examen ni integracion API externa en esta fase.
- Actividades `ACT_XXXX` se crean para sprint actual priorizando primero HU_01/HU_02/HU_03.

---

## HU_07 - Validar conectividad LAN entre app movil y backend local
**Como** desarrollador en fase MVP
**Quiero** probar desde el celular que la app puede conectarse al backend por IP local
**Para** confirmar viabilidad de pruebas reales antes de integrar lectura de foto completa.

### Criterios de aceptacion
1. La app movil puede consultar un endpoint de salud (`health`) del backend usando IP local.
2. Se documenta resultado de prueba en la misma red LAN (exito o fallo con causa).
3. Se define checklist minimo de red local para repetir la prueba.

### Evidencia esperada
- Pantalla/componente de prueba de conectividad en app movil.
- Registro de prueba LAN ejecutada contra backend local.

---

## HU_08 - Recibir foto desde app movil y procesar lectura en backend
**Como** backend OMR
**Quiero** recibir una foto enviada desde la app movil y ejecutar el pipeline de lectura
**Para** devolver JSON de respuestas sin depender de carga manual en disco.

### Criterios de aceptacion
1. Existe endpoint que recibe imagen y metadata/template de referencia.
2. El endpoint responde JSON estructurado por pregunta con estados de opciones.
3. Errores de entrada (imagen invalida, marcadores faltantes) se retornan de forma legible.

### Evidencia esperada
- Endpoint FastAPI documentado para carga de imagen.
- Prueba local de envio y respuesta JSON valida.

---

## HU_09 - Capturar foto en app Expo y mostrar resultado JSON
**Como** usuario de prueba MVP
**Quiero** tomar una foto de la hoja desde el celular y enviarla al backend
**Para** ver de inmediato las opciones detectadas por pregunta.

### Criterios de aceptacion
1. La app Expo activa camara y captura una foto.
2. La foto se envia al backend local y recibe respuesta JSON.
3. La app muestra resultado legible (al menos resumen + JSON crudo).

### Evidencia esperada
- Pantalla Expo con captura y envio.
- Resultado mostrado en dispositivo tras procesar una foto real.

