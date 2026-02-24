# HU_003 - Historias de Usuario de EP_001 (Motor alterno de lectura LLM Gemini)

## Trazabilidad
- Epica asociada: `EP_001_lectura_movil_local_omr_a_json.md`
- Historias previas relacionadas:
  - `HU_001_EP_001_lectura_movil_local_omr_a_json.md`
  - `HU_002_EP_001_mejoras_robustez_lectura_omr.md`
- Decision de negocio/tecnica: mantener motor clasico y agregar motor alterno `gemini` bajo una interfaz comun.

## HU_13 - Habilitar motor alterno Gemini sin romper contrato de salida
**Como** equipo de backend OMR  
**Quiero** agregar un motor alterno de lectura con Gemini 1.5 Pro  
**Para** comparar su desempeño contra el motor clasico manteniendo el mismo JSON de salida.

### Criterios de aceptacion
1. Existe una interfaz de lectura comun (`reader`) con implementacion clasica y Gemini.
2. El endpoint actual conserva la misma estructura de salida para ambos motores.
3. La seleccion de motor se controla por configuracion (`classic` o `gemini`) sin editar codigo.
4. Si Gemini falla (timeout, cuota o salida invalida), el backend responde error controlado y trazable.

### Evidencia esperada
- Modulos backend desacoplados por estrategia de lector.
- Configuracion documentada para activar motor.
- Ejecucion manual valida con ambos motores sobre una misma imagen.

---

## HU_14 - Benchmark comparativo classic vs gemini con dataset real
**Como** equipo tecnico  
**Quiero** ejecutar un benchmark reproducible con imagenes reales  
**Para** decidir con datos el motor por defecto en siguientes iteraciones.

### Criterios de aceptacion
1. Existe script/comando para ejecutar lote de imagenes con ambos motores.
2. Se reporta por imagen: exactitud, preguntas vacias, ambiguas, tiempo de respuesta y errores.
3. Se genera resumen global comparativo y archivo exportable (`JSON` o `CSV`).
4. Se mantiene referencia de verdad-terreno usada para comparar resultados.

### Evidencia esperada
- Reporte comparativo en `src/backend/data/output`.
- Resumen utilizable en bitacora para decision de siguiente sprint.

---

## HU_15 - Operacion segura del motor Gemini para MVP
**Como** responsable del sistema  
**Quiero** controles minimos operativos para uso de Gemini  
**Para** evitar fallos silenciosos, costos no controlados y salidas no parseables.

### Criterios de aceptacion
1. El backend valida y normaliza salida estructurada de Gemini antes de responder.
2. El backend registra metricas minimas por solicitud (duracion, motor usado, estado final).
3. Se documentan variables requeridas (`API key`, modelo, timeout).
4. Existe politica de fallback definida (solo error controlado o fallback a clasico, segun configuracion).

### Evidencia esperada
- Validadores de salida en backend.
- Logs con trazabilidad por solicitud.
- Seccion tecnica en README/backend con prerequisitos de ejecucion.

## Notas de alcance para sprint
- Este bloque habilita evaluacion comparativa, no reemplazo definitivo del motor clasico.
- Se mantiene la regla de ArUco obligatorio para flujo clasico.
- Las mejoras de robustez de `HU_002` quedan pausadas temporalmente mientras se implementa el enfoque alterno.
