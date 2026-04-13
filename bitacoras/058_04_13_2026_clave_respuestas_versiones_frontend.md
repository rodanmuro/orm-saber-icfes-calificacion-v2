# Bitacora 058_04_13_2026 08:43:42 clave_respuestas_versiones_frontend

## Que fue lo que se hizo
- Se implemento en el frontend de Armado de examen la consulta de respuestas correctas por version publicada (no por examen base).
- Se agrego una accion en la tabla de versiones publicadas: boton `Ver respuestas correctas`.
- Se agrego un modal de clave con contexto de examen/version y tabla de resultados por pregunta.
- Se incorporo flujo de carga para la consulta de clave (`Consultando...`) mientras llega la respuesta del backend.
- Se reutilizo el endpoint existente de detalle de version para construir la clave real barajada (`correct_answer_mapped`) sin cambios de base de datos.
- Archivos modificados:
  - `src/frontend_web/src/App.jsx`
  - `src/frontend_web/src/components/ExamBuilder.jsx`
  - `src/frontend_web/src/styles.css`

## Para que se hizo
- Permitir al docente conocer la clave real de una version publicada, que puede diferir de la clave original por el barajado de preguntas y opciones.
- Reducir errores operativos al revisar resultados o al preparar procesos de calificacion posteriores.

## Que problemas se presentaron
- Riesgo de ambiguedad funcional: un boton en tabla de examenes podia inducir a mostrar una clave incorrecta o no asociada a una version concreta.
- Necesidad de mantener coherencia con el comportamiento actual del sistema, donde las exportaciones (PDF/DOCX) ya se orientan a versiones publicadas.

## Como se resolvieron
- Se movio la accion al lugar correcto: tabla de `Versiones publicadas`.
- Se implemento lectura de detalle de version y extraccion de `question_number` + `correct_answer_mapped` + `item_id`, ordenando por numero de pregunta.
- Se agrego modal dedicado para visualizacion clara de la clave y datos de contexto (version code y seed).
- Se validaron cambios con build del frontend (`npm run build`) exitoso.

## Que continua
- Agregar boton `Copiar clave` en el modal en formato compacto (por ejemplo `1:A, 2:C, ...`).
- Evaluar exportacion de clave a TXT/CSV para uso administrativo.
- Definir control de acceso para que solo perfiles autorizados visualicen la clave.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
