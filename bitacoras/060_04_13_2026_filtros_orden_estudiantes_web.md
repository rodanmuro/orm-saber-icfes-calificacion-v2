# Bitacora 060_04_13_2026 10:55:53 filtros_orden_estudiantes_web

## Que fue lo que se hizo
- Se agregaron filtros y ordenamiento a la pestaña "Estudiantes" en el frontend web.
- Se implemento filtro por texto libre (nombre, correo, documento, UUID, grupo) y filtro por grupo.
- Se agrego selector de ordenamiento (ID, apellido, grupo, documento).
- Archivos modificados:
  - `src/frontend_web/src/App.jsx`
  - `src/frontend_web/src/components/StudentList.jsx`

## Para que se hizo
- Para facilitar la busqueda rapida de estudiantes y mejorar la usabilidad del listado.
- Para soportar el uso operativo de grupos y grandes volumenes de estudiantes.

## Que problemas se presentaron
- No habia filtros ni ordenamiento en la vista inicial, lo que hacia lenta la busqueda manual.

## Como se resolvieron
- Se implementaron filtros en el contenedor de la pestaña y se aplico logica de filtrado/ordenamiento en `StudentList`.
- Se valido el build del frontend con `npm run build`.

## Que continua
- Evaluar paginacion cuando el numero de estudiantes crezca.
- Agregar exportacion CSV desde el listado si se requiere.

*(Agregar enlaces a archivos clave o referencias adicionales si aplica.)*
