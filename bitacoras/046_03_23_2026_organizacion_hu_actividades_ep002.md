# Bitacora 046_03_23_2026 11:30:29 organizacion_hu_actividades_ep002

## Que fue lo que se hizo
- Se reorganizaron historias de usuario y actividades de `EP_002` para que la planeacion quede alineada con lo que ya esta funcionando en el editor web y en el asistente IA.
- Se actualizaron las HU para dejar explicitos criterios que ya estaban implementados:
  - `planeacion/01_historias_de_usuario/HU_005_EP_002_banco_items_docente_web.md`
  - `planeacion/01_historias_de_usuario/HU_015_EP_002_asistente_ia_generacion_items.md`
- Se cerraron y normalizaron actividades que estaban desfasadas en estado/nombre de archivo:
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0040_HU_05_EP_002_DONE.md` (nuevo, reemplaza TODO)
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0048_HU_12_EP_002_DONE.md` (nuevo, reemplaza TODO)
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0049_HU_12_EP_002_DONE.md` (nuevo, reemplaza TODO)
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0057_HU_15_EP_002_DONE.md` (renombre desde TODO)
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0058_HU_15_EP_002_DONE.md` (renombre desde TODO)
- Se actualizo `ACT_0059` para registrar explicitamente avances recientes de robustez IA:
  - `planeacion/02_actividades/epicas/EP_002_banco_items_y_generacion_examenes_web/ACT_0059_HU_15_EP_002_TODO.md`
  - Se marcaron como hechos: parseo robusto de JSON con ruido y normalizacion de variantes `media_spec`.

## Para que se hizo
- Para que la documentacion de planeacion represente el estado real del producto y no genere confusion en siguientes iteraciones.
- Para facilitar priorizacion de trabajo pendiente real (lo no implementado), separandolo claramente de lo ya entregado.
- Para mejorar trazabilidad de decisiones frente a UX del editor (imagenes/ecuaciones) y estabilidad del modulo IA.

## Que problemas se presentaron
- Se encontro inconsistencia entre estado interno de actividades (`estado: done`) y nombre de archivo (`_TODO.md`).
- Existia deuda de trazabilidad: algunos ajustes recientes de estabilidad IA ya estaban en codigo, pero no estaban reflejados en actividades.
- Durante la operacion de consola, el sandbox local fallo con `bwrap: Unknown option --argv0`, impidiendo comandos normales de inspeccion/edicion.

## Como se resolvieron
- Se normalizo la planeacion en dos niveles:
  - Criterios de HU actualizados.
  - Actividades cerradas/renombradas cuando correspondia, y actividad en progreso ajustada con checks concretos.
- Se mantuvo `ACT_0059` en `en_progreso` para no sobredeclarar cierre; solo se marcaron como completados los puntos efectivamente implementados.
- Se sustituyeron archivos `_TODO` por `_DONE` en actividades cerradas para consistencia visual y operativa en revisiones futuras.
- Para el bloqueo de `bwrap`, se ejecuto la operacion fuera del sandbox, permitiendo terminar la sincronizacion documental sin afectar codigo de negocio.

## Que continua
- Completar pendientes de `ACT_0059`:
  - test de contrato de proveedor OpenAI,
  - E2E generar -> aplicar -> guardar,
  - documentacion final en README backend/frontend sobre `.env`, costos/tokens y responsabilidades de revision docente.
- Mantener la regla de consistencia: cuando una actividad cambie a `done`, sincronizar tambien su nombre de archivo.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
