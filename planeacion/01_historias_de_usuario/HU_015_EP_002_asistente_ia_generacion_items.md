# HU_015 - Asistente IA en editor de items (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Dependencias: `HU_005`, `HU_012`.

## Historia de usuario
**Como** docente  
**Quiero** un asistente IA en la pantalla de edicion de items para conversar y generar borradores de preguntas  
**Para** acelerar la creacion de preguntas de seleccion multiple alineadas al estandar y competencia curricular.

## Criterios de aceptacion
1. El asistente se muestra en la vista `Editar item` con un cuadro de entrada y salida tipo chat corto.
2. Antes de generar, deben estar definidos al menos `standard_name` y `competency_name` en el formulario.
3. El backend consume OpenAI via endpoint interno y retorna salida estructurada: `statement`, `options(A-D)`, `correct_answer`, `metadata`, `usage`.
4. Al generar, el borrador se aplica al formulario (`enunciado`, `opciones`, `respuesta correcta`) sin guardado automatico en base de datos.
5. El sistema valida que la salida de IA cumpla formato esperado (4 opciones A/B/C/D y una sola correcta), y normaliza la correcta en `A`.
6. El item guardado conserva trazabilidad en metadata (`ai_generated`, `ai_model`, `ai_prompt_version`).
7. La interfaz muestra consumo por peticion: tokens de entrada/salida/cached y costo USD calculado.
8. Ante errores de IA o formato invalido, se informa mensaje claro sin romper la edicion manual.
9. La generacion de IA tolera variantes de `media_spec` (`data`, `values`, `sizes`) y normaliza al contrato interno esperado.
10. El parseo de salida IA es robusto a ruido de texto y mantiene salida JSON estructurada para el frontend.

## Evidencia esperada
- Flujo funcional en frontend: conversar -> generar -> aplicar al formulario.
- Endpoint backend de generacion IA validado con pruebas.
- Evidencia de item guardado con metadata de origen IA.
- Evidencia visual de costos/tokens por peticion IA.

## Notas
- El alcance inicial es asistencia de borrador; la revision docente sigue siendo obligatoria.

## Guardrails obligatorios
- No se guarda automaticamente ningun item generado por IA; siempre requiere confirmacion manual del docente.
- El asistente solo genera items de seleccion multiple con 4 opciones (A/B/C/D) y una sola respuesta correcta.
- La generacion se bloquea si no hay contexto curricular minimo (`standard_name` y `competency_name`).
- Toda generacion aplicada debe quedar trazable en metadata (`ai_generated`, `ai_model`, `ai_prompt_version`).
- Errores de proveedor o formato deben mostrarse de forma controlada sin afectar la edicion manual.
