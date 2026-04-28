# Bitacora 065_04_28_2026 13:01:47 analiticas_modal_marcadas

## Que fue lo que se hizo
- Se extendio la pestana de Analiticas para incluir analisis de respuestas marcadas por pregunta (distractores) con un modal por fila.
- Se modifico `src/frontend_web/src/App.jsx` para calcular y consolidar distribucion de marcadas por pregunta a partir de los intentos filtrados:
  - Conteos por opcion `A/B/C/D`.
  - Conteo de `blank` (no marcada).
  - Conteo de `ambiguous` (marcado ambiguo o multiple).
  - Total de marcaciones por pregunta (`markedTotal`).
- Se modifico `src/frontend_web/src/components/AnalyticsPanel.jsx` para:
  - Agregar columna `Marcadas` en la tabla de resultados por pregunta.
  - Agregar boton `Ver` por fila que abre modal con distribucion (cantidad y porcentaje).
  - Mantener la vista de pregunta (`Ver`) ya implementada para revisar enunciado y opciones.
- Se validaron los cambios con compilacion de frontend (`npm run build`) sin errores.

## Para que se hizo
- Permitir analisis pedagogico por distractor en cada pregunta.
- Facilitar deteccion de patrones de error (por ejemplo, opcion incorrecta mas seleccionada) para retroalimentacion y mejora de items.

## Que problemas se presentaron
- Hubo una primera aplicacion de parche que no encontro contexto exacto en `AnalyticsPanel.jsx` por diferencia en bloques de renderizado actuales.
- No se detectaron fallos de compilacion luego de ajustar el parche al contenido real del archivo.

## Como se resolvieron
- Se releyo el archivo completo `src/frontend_web/src/components/AnalyticsPanel.jsx` para aplicar un parche con contexto correcto.
- Se incorporo el estado local del modal de marcadas y su render condicional.
- Se agrego el enriquecimiento de datos en `App.jsx` durante `refreshAnalytics()` para enviar al panel:
  - `markedDistribution` por pregunta.
  - `markedTotal` por pregunta.
- Se ejecuto build de frontend para verificar integridad funcional del cambio.

## Que continua
- Evaluar agregar ordenamiento directo por opcion marcada dominante (A/B/C/D/blank/ambiguous).
- Evaluar exportar estas analiticas (tabla de distractores) a CSV/PDF para uso docente.
- Si se requiere, agregar resaltado visual de la opcion incorrecta dominante en la tabla principal.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
