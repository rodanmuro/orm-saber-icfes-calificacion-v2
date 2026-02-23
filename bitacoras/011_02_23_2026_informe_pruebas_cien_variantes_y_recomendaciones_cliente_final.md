# Bitacora 011_02_23_2026 12:01:07 informe_pruebas_cien_variantes_y_recomendaciones_cliente_final

## Que fue lo que se hizo
- Se ejecuto una campaña de pruebas masivas con 100 variantes sinteticas de una foto real diligenciada para evaluar robustez de lectura OMR.
- Se implemento un benchmark reproducible que aplica transformaciones por imagen (rotacion, desenfoque, ruido, brillo/contraste y compresion JPEG), ejecuta lectura completa y compara contra clave validada manualmente.
- Se genero evidencia estructurada por imagen y reportes consolidados en JSON y HTML para facilitar analisis.
- Se conservaron los reportes y se ajusto `.gitignore` para no versionar imagenes pesadas de pruebas.
- Archivos clave creados/modificados:
  - `src/backend/app/modules/omr_reader/scripts/benchmark_cien_pruebas.py`
  - `src/backend/data/input/diligenciadas/cien_pruebas/resultados/reporte_cien_pruebas.json`
  - `src/backend/data/input/diligenciadas/cien_pruebas/resultados/reporte_cien_pruebas.html`
  - `.gitignore`

## Para que se hizo
- Cuantificar el comportamiento real del lector antes de integracion movil.
- Extraer recomendaciones claras para el usuario final sobre como tomar fotos para reducir errores de lectura.

## Que problemas se presentaron
- En una parte de los casos hubo fallo de pipeline porque no se detecto el marcador ArUco de esquina inferior derecha.
- En otras imagenes, aunque si hubo deteccion ArUco, aparecieron diferencias de respuestas por degradacion visual (combinaciones de giro alto, blur y ruido).
- Se identifico concentracion de errores en ciertas preguntas (especialmente 23, 25 y 26), lo que sugiere sensibilidad local bajo degradaciones fuertes.

## Cifras obtenidas en el experimento
- Total evaluado: 100 variantes sinteticas de una foto real.
- Resultado global:
  - 76 casos exactos (sin diferencias contra la clave).
  - 16 casos con diferencias de respuestas.
  - 8 casos con error de pipeline por ArUco faltante.
- Exactitud promedio por pregunta en el lote completo: 0.8657.
- Relacion entre angulo y fallas:
  - En rango absoluto 0-5 grados: 0 fallas.
  - En rango absoluto 5-10 grados: 3 fallas (solo mismatches).
  - En rango absoluto 10-15 grados: 21 fallas (13 mismatches + 8 errores ArUco).
  - Todos los errores de ArUco ocurrieron entre ~13.1 y ~14.8 grados.
- Comportamiento por tipo de fallo:
  - Mismatch: ruido promedio ~11.24 y blur predominante en kernel 3/7.
  - Pipeline ArUco: giro promedio ~14.0 grados.
- Preguntas mas sensibles en mismatches:
  - 25 (16 veces), 26 (16), 23 (15), luego 16 y 19 (9 cada una).

### Mini-tabla de lectura rapida

| Indicador | Valor |
|---|---|
| Total de variantes | 100 |
| Casos exactos | 76 |
| Casos con mismatch | 16 |
| Errores de pipeline (ArUco) | 8 |
| Exactitud promedio | 0.8657 |
| Fallas con \|angulo\| 0-5 | 0 |
| Fallas con \|angulo\| 5-10 | 3 |
| Fallas con \|angulo\| 10-15 | 21 |
| Rango de angulo con fallas ArUco | ~13.1 a ~14.8 |
| Preguntas mas sensibles | 25, 26, 23, 16, 19 |

## Como se resolvieron
- Se separaron y clasificaron fallos en dos grupos:
  - fallo de alineacion por ArUco no detectable,
  - mismatch de respuestas con pipeline completo.
- Se registro trazabilidad por imagen con parametros exactos de transformacion (`angle_deg`, `blur_kernel`, `noise_sigma`, `alpha`, `beta`, `jpeg_quality`) para permitir reproducibilidad.
- Se consolidaron recomendaciones operativas para captura:
  - evitar inclinaciones fuertes al tomar foto,
  - asegurar que los 4 marcadores ArUco se vean completos,
  - evitar desenfoque por movimiento,
  - mantener iluminacion uniforme sin sombras sobre la hoja.

## Que continua
- Definir umbrales de aceptacion operativa (calidad minima de captura) para guiar al usuario antes de procesar.
- Implementar mejoras de robustez (preprocesamiento y ajuste de umbrales) y re-ejecutar el benchmark para medir mejora.
- Incorporar una guia corta para cliente final de "como tomar la foto" basada en este informe.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
