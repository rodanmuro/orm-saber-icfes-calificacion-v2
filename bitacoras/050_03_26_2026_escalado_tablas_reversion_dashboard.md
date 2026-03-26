# Bitacora 050_03_26_2026 10:33:26 escalado_tablas_reversion_dashboard

## Que fue lo que se hizo
- Se reviso el alineamiento entre epicas, historias de usuario y actividades para EP_002, y se agregaron nuevas actividades de continuidad:
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0060_HU_05_EP_002_DONE.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0061_HU_05_EP_002_DONE.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0062_HU_05_EP_002_DONE.md`
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0063_HU_15_EP_002_IN_PROGRESS.md`
- Se intento mejorar el escalado de tablas en el editor Tiptap mediante ajustes CSS sobre `.tableWrapper` y `table`.
- Se corrigio un problema de datos que generaba tablas descuadradas por "columnas fantasma" en el JSON de salida IA:
  - Normalizacion en backend para recortar celdas vacias en bordes y balancear columnas por fila.
  - Archivos modificados:
    - `src/backend/app/modules/item_ai_assistant/service.py`
    - `src/backend/tests/test_item_ai_assistant_service.py`
- Se revirtieron cambios de escalado que no resolvieron el comportamiento esperado.
- Se restauro la experiencia dashboard para no perder navegacion lateral fija (sidebar izquierda sticky), corrigiendo regresion visual en frontend.
  - Archivo ajustado: `src/frontend_web/src/styles.css`

## Para que se hizo
- Mantener trazabilidad real del avance de planeacion frente a lo ya implementado.
- Resolver el problema reportado por el cliente en tablas: descuadre estructural y escalado no funcional.
- Evitar degradar UX general (sidebar fija y layout dashboard) durante pruebas de escalado.

## Que problemas se presentaron
- El escalado de tablas en Tiptap no quedo funcional en terminos de UX final, aunque hubo cambios en CSS.
- Se introdujo una regresion al revertir archivos de frontend: se perdieron estilos del dashboard/sidebar al restaurar de forma amplia.
- Se detecto que una parte del problema no era solo CSS: habia tablas con estructura inconsistente (columna vacia adicional) provenientes del contenido generado.

## Como se resolvieron
- Se separo el problema en dos capas:
  - Capa de datos (backend): se normalizaron tablas para evitar columnas vacias de borde y forzar consistencia entre filas.
  - Capa de presentacion (frontend): se deshicieron intentos de escalado no confiables para no dejar UX inestable.
- Se agrego prueba automatica de regresion para el caso de tabla con columnas fantasma.
- Se restauro explicitamente el bloque de estilos dashboard (incluyendo sidebar sticky) para recuperar el estado visual correcto sin reintroducir los cambios de escalado fallidos.

## Que continua
- Implementar una solucion robusta de escalado de tabla a nivel editor (NodeView/extension dedicada), no solo con CSS.
- Mantener el resize por columnas como comportamiento estable mientras se implementa el escalado global real.
- Completar `ACT_0063` con pruebas y documentacion de estabilidad del contrato IA.
- Validar en sesion controlada los siguientes criterios de UX para tablas:
  - Escalado global predecible.
  - Edicion de celdas sin overlays indeseados.
  - Sin regresiones en sidebar/dashboard.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
