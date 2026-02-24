# Bitacora 018_02_23_2026 22:13:24 replanificacion_hu003_y_acts_bloqueadas

## Que fue lo que se hizo
- Se ajusto la epica `EP_001` para reflejar el nuevo enfoque de motor alterno: la app envia la imagen al backend y el backend delega al motor configurado (`classic` o LLM de vision como Gemini).
- Se creo una nueva historia de usuario para este frente:
  - `planeacion/01_historias_de_usuario/HU_003_EP_001_motor_alterno_lectura_llm_gemini.md`
- Se crearon nuevas actividades para HU_13, HU_14 y HU_15:
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0022_HU_13_EP_001_TODO.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0023_HU_13_EP_001_TODO.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0024_HU_13_EP_001_TODO.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0025_HU_14_EP_001_TODO.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0026_HU_15_EP_001_TODO.md`
- Se pausaron temporalmente actividades de robustez previas y se reflejo estado `BLOCKED` en nombre y contenido:
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0017_HU_10_EP_001_BLOCKED.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0018_HU_10_EP_001_BLOCKED.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0019_HU_11_EP_001_BLOCKED.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0020_HU_11_EP_001_BLOCKED.md`
  - `planeacion/02_actividades/epicas/EP_001_lectura_movil_local_omr_a_json/ACT_0021_HU_12_EP_001_BLOCKED.md`
- Se actualizo la trazabilidad de la investigacion en:
  - `bitacoras/017_02_23_2026_investigacion_referentes_omr_fuentes_y_decisiones_adopcion.md`

## Para que se hizo
- Reordenar el backlog segun prioridad de sprint y habilitar comparacion real `classic vs gemini` sin perder el trabajo previo de OMR clasico.
- Mantener coherencia con la metodologia Scrum del proyecto: IDs estables, estados en nombre y contenido, y trazabilidad entre epica/HU/actividades/bitacora.

## Que problemas se presentaron
- Se identifico incoherencia entre el nuevo frente y referencias existentes en bitacoras/planeacion (actividades figuraban como `TODO` cuando ya debian quedar pausadas).
- Habia riesgo de confusion de alcance en EP_001 sobre donde ocurre el procesamiento (app vs backend).

## Como se resolvieron
- Se normalizo el estado de las actividades de robustez a `BLOCKED` y se agrego nota de pausa en cada archivo afectado.
- Se redacto HU_003 con criterios de aceptacion centrados en contrato estable, selector de motor y benchmark comparativo.
- Se agregaron actividades concretas para implementacion incremental del motor alterno y control operativo.
- Se ajusto texto de EP_001 para aclarar que la delegacion al motor ocurre en backend.

## Que continua
- Ejecutar `ACT_0022` para formalizar interfaz comun de lector y adaptador del motor clasico.
- Ejecutar `ACT_0023` para integrar el lector Gemini con validacion de salida estructurada.
- Ejecutar `ACT_0025` para comparar ambos motores con metrica objetiva sobre dataset real.
- Reabrir `ACT_0017` a `ACT_0021` cuando cierre el primer ciclo comparativo y se decida siguiente iteracion de robustez.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
