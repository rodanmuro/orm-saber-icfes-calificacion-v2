# Bitacora 009_02_23_2026 11:08:48 informe_pruebas_deteccion_aruco_y_recomendaciones_toma_imagenes

## Que fue lo que se hizo
- Se ejecutaron pruebas reales de deteccion de ArUco y alineacion de perspectiva sobre fotos tomadas manualmente.
- Se renombraron imagenes de entrada para simplificar ejecucion y trazabilidad:
  - `src/backend/data/input/foto_001.jpeg` ... `foto_005.jpeg`
- Se ejecutaron pruebas de alineacion sobre las 5 fotos reales con resultado exitoso en todos los casos.
- Se creo una carpeta de pruebas masivas ignorada por git:
  - `src/backend/data/input/cien_pruebas/`
- Se actualizo `.gitignore` para evitar versionar ese volumen de imagenes de prueba.
- Se genero un lote de 100 imagenes derivadas de las 5 fotos base para pruebas de estres.
- Se ejecuto prueba masiva inicial (copias sin degradacion) con resultado 100/100 exitoso.
- Se repitio el experimento con degradaciones sinteticas (ruido, desenfoque, rotacion y variacion de brillo/contraste) sobre 100 imagenes.
- Se midio resultado del lote degradado y se analizaron fallos por archivo y causa.

## Para que se hizo
- Evaluar de forma objetiva la robustez de deteccion ArUco bajo condiciones reales y perturbadas.
- Establecer una linea base de desempeno para la epica de lectura local OMR antes de implementar clasificacion de burbujas.
- Identificar recomendaciones de captura para mejorar tasa de exito en campo.

## Que problemas se presentaron
- En el lote degradado de 100 imagenes hubo 19 fallos de deteccion.
- Todos los fallos ocurrieron porque faltaba al menos un marcador ArUco requerido para alinear.
- Los marcadores mas afectados en este experimento fueron:
  - `id 3` (esquina `bottom_right`) con mayor frecuencia,
  - luego `id 0` (`top_left`),
  - y en menor medida `id 2` (`bottom_left`).

## Como se resolvieron
- Se extrajo listado completo de archivos fallidos y motivo exacto por archivo.
- Se confirmo que no hubo fallos de metadata ni de homografia cuando los 4 marcadores estaban presentes.
- Se consolidaron recomendaciones de captura para reducir perdida de marcadores.

## Que continua
- Avanzar con `ACT_0009` para lectura de burbujas sobre imagenes ya alineadas.
- Mantener pruebas de precision con dos niveles:
  - set real sin degradacion,
  - set degradado para prueba de robustez.
- Definir recomendaciones operativas para toma de imagenes en campo:
  - asegurar visibilidad completa de los 4 ArUco,
  - evitar recorte de esquinas,
  - mantener buena iluminacion uniforme,
  - evitar desenfoque por movimiento,
  - evitar angulos extremos que deformen marcadores,
  - revisar nitidez antes de procesar.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
