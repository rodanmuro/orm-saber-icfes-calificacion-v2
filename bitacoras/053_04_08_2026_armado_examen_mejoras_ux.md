# Bitacora 053_04_08_2026 07:46:53 armado_examen_mejoras_ux

## Que fue lo que se hizo
- Se ajusto el flujo de creacion de examenes para reducir errores manuales en codificacion:
  - `exam_code` paso a opcional en request y se autogenera secuencial por docente (`1`, `2`, `3`, ...).
  - Archivos backend modificados:
    - `src/backend/app/schemas/exam_bank.py`
    - `src/backend/app/api/v1/endpoints/exams.py`
- Se corrigio visualizacion de enunciados en la seccion de armado de examen:
  - Se elimino el render de JSON crudo y se mostro vista textual resumida.
  - Se evito recorte de botones de accion en tablas.
  - Archivos frontend modificados:
    - `src/frontend_web/src/components/ExamBuilder.jsx`
    - `src/frontend_web/src/styles.css`
- Se implemento vista previa enriquecida en modal por fila:
  - Boton `Vista previa` en items disponibles y asociados.
  - Render de enunciado y opciones A/B/C/D en modo solo lectura, soportando imagenes, ecuaciones y tablas.
  - Navegacion contextual en modal (`Anterior`/`Siguiente`) segun origen:
    - por asignar
    - asignados
  - Archivo frontend creado:
    - `src/frontend_web/src/components/RichDocPreview.jsx`
- Se agregaron columnas informativas en tablas de armado:
  - `Estandar`
  - `Desempeño`
  - Enunciado/Estandar/Desempeño con truncado + tooltip para texto completo.
- Se agrego scroll vertical independiente para los paneles:
  - `Items disponibles`
  - `Items asociados`
- Se movio `Armado de examen` a una pestaña independiente en sidebar, separandolo de `Editar item` y `Listado`.
  - Archivo modificado: `src/frontend_web/src/App.jsx`
- Se retiro el boton `Recargar examenes` y se cambio por carga automatica:
  - al entrar a la pestaña
  - al cambiar `Teacher ID`.
- Se hicieron consultas SQL de diagnostico y saneamiento de datos en PostgreSQL local:
  - Se detecto mezcla de items por `teacher_id` (1 y 5).
  - Se reasignaron items a `teacher_id=1` para unificar el banco en uso.

## Para que se hizo
- Mejorar usabilidad del armado de examen para trabajo operativo real con volumen de preguntas.
- Reducir errores de usuario en codificacion de examenes OMR.
- Aumentar trazabilidad visual de preguntas y metadatos curriculares antes de asociar.
- Evitar friccion por acciones manuales innecesarias (recarga de examenes).

## Que problemas se presentaron
- Error `HTTP 422` al asociar items por discrepancia de docente entre examen e item.
- Desfase percibido entre total de items y disponibles por filtro implicito de docente.
- Enunciados en tablas del armado mostraban JSON en bruto, no contenido legible.
- El bloque de armado convivia en la misma pantalla que edicion/listado y generaba sobrecarga visual.

## Como se resolvieron
- Se reforzo filtro en frontend para listar solo items del mismo docente del examen seleccionado.
- Se verifico con consultas SQL el estado real de datos y se realizo correccion controlada de `teacher_id` en items.
- Se implemento preview textual con truncado y tooltip en tablas, y preview enriquecido en modal para inspeccion completa.
- Se reestructuro navegacion por pestañas para separar claramente:
  - Edicion de item
  - Listado de items
  - Armado de examen
- Se automatizo carga de examenes por `Teacher ID` para eliminar dependencia del boton de recarga.

## Que continua
- Implementar agregado masivo aleatorio de N preguntas respetando no repeticion en examen.
- Exponer contador global mas explicito por docente en armado (ej. total docente, asociados, disponibles).
- Definir flujo de seleccion de cantidad objetivo de preguntas al crear examen (ej. 40 por defecto configurable).
- Registrar prueba E2E formal del flujo: crear examen -> asociar -> publicar version -> validar answer key.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
