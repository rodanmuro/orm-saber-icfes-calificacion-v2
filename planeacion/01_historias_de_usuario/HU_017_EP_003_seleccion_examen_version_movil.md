# HU_017 - Seleccion de examen y version en interfaz movil (EP_003)

## Trazabilidad
- Epica asociada: `EP_003_calificacion_omr_versionada_por_docente.md`
- Dependencias: `HU_007_EP_003_calificacion_omr_por_version_y_docente.md`

## Historia de usuario
**Como** docente que usa la app movil
**Quiero** seleccionar el examen y su version publicada antes de calificar
**Para** asegurar que la lectura OMR se compare con la clave correcta.

## Criterios de aceptacion
1. La interfaz movil lista examenes disponibles para el docente por defecto.
2. Cada examen muestra sus versiones publicadas disponibles para seleccionar.
3. El usuario selecciona examen + version y luego envia la captura para calificar.
4. Si no hay versiones publicadas, el flujo bloquea la calificacion con mensaje claro.
5. El backend recibe `exam_id` y `version_id` (o equivalente) con el intento OMR.

## Evidencia esperada
- Pantallas de seleccion de examen/version en movil.
- Payload enviado al backend con identificadores de examen y version.
- Prueba manual con calificacion exitosa usando version seleccionada.

## Notas
- En este incremento no se implementan perfiles; el docente es por defecto.
- La lista puede filtrarse por docente si ya existe `teacher_id` en el backend.
