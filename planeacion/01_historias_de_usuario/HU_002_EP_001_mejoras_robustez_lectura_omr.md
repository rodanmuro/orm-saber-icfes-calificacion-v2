# HU_002 - Historias de Usuario de EP_001 (Mejoras de robustez en lectura OMR)

## Trazabilidad
- Epica asociada: `EP_001_lectura_movil_local_omr_a_json.md`
- Documento base previo: `HU_001_EP_001_lectura_movil_local_omr_a_json.md`
- Alcance de esta fase: mejorar robustez de lectura en imagenes reales, manteniendo ArUco 4/4 obligatorio.

## HU_10 - Mejorar preprocesamiento para reducir ambiguas y vacias
**Como** modulo de lectura OMR  
**Quiero** evaluar una variante adicional de preprocesamiento robusto (`CLAHE -> GaussianBlur(5x5) -> OTSU_INV`)  
**Para** reducir preguntas ambiguas y no detectadas en fotos reales de celular.

### Criterios de aceptacion
1. Existe al menos una variante adicional de preprocesamiento integrada al pipeline OMR.
2. La variante puede ejecutarse de forma controlada/configurable sin romper el flujo actual.
3. Se conserva trazabilidad de salida para comparar resultados entre variantes.

### Evidencia esperada
- Cambios en backend de lectura OMR.
- Ejecuciones comparativas sobre imagenes reales con salida verificable.

---

## HU_11 - Seleccionar automaticamente variante de lectura por metricas
**Como** motor de lectura  
**Quiero** seleccionar la mejor variante de preprocesamiento por metricas objetivas  
**Para** obtener mayor estabilidad en deteccion sin calibracion manual por imagen.

### Criterios de aceptacion
1. El sistema calcula metricas comparables por variante (ej: ambiguas y separacion top1-top2).
2. Se aplica una regla determinista para elegir variante ganadora.
3. El resultado final expone en diagnosticos que variante fue seleccionada.

### Evidencia esperada
- Regla de seleccion implementada y documentada.
- Pruebas sobre lote de imagenes con reporte de comportamiento.

---

## HU_12 - Exponer senales de confianza para soporte de revision manual futura
**Como** consumidor de resultados OMR  
**Quiero** recibir senales de confianza por pregunta  
**Para** identificar casos dudosos y habilitar un flujo de correccion manual en fases siguientes.

### Criterios de aceptacion
1. La salida por pregunta incluye metrica de confianza (ej: margen top1-top2).
2. Se identifica explicitamente si la pregunta queda en baja confianza.
3. El resumen global incluye conteo de preguntas de baja confianza.

### Evidencia esperada
- JSON de salida con nuevos campos de diagnostico por pregunta.
- Evidencia en pruebas reales donde se identifiquen casos de baja confianza.

---

## Notas de alcance para sprint
- No incluye calificacion final de examen (score); solo mejora de lectura y confianza.
- No incluye fallback sin ArUco; se mantiene politica de 4 marcadores obligatorios.
- No incluye aun dashboard frontend de revision manual; queda como deuda tecnica de fase posterior.
