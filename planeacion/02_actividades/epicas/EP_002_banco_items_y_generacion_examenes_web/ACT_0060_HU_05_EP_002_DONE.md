estado: done
prioridad: alta
sprint: S8
owner: por_definir

# ACT_0060 - Borrado masivo y forzado de items con manejo de dependencias

## Objetivo tecnico
Habilitar una operacion segura y trazable para eliminar multiples items desde el listado, incluyendo casos con dependencias referenciales a examenes/versiones.

## Tareas implementables
- [ ] Agregar seleccion multiple por checkboxes en el listado de items.
- [ ] Implementar accion de borrado masivo con confirmacion previa.
- [ ] Reportar resultado por item (eliminado / no eliminado) en la respuesta visual del frontend.
- [ ] Manejar `409` por dependencias activas con mensaje claro para usuario.
- [ ] Implementar flujo de `forzar borrado` que use `DELETE /items/{id}?force=true` con confirmacion reforzada.
- [ ] Agregar pruebas backend para:
  - caso `DELETE` sin `force` con dependencias (respuesta `409`),
  - caso `DELETE` con `force=true` (eliminacion controlada).

## Evidencias esperadas
- Flujo funcional de borrado masivo desde UI web.
- Evidencia de manejo correcto de errores por integridad referencial.
- Pruebas automatizadas en verde para borrado normal y forzado.

## Criterio de terminado
El docente puede eliminar lotes de items desde el listado, con control explicito de riesgos y trazabilidad de cada resultado.

