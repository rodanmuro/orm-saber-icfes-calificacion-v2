estado: todo
prioridad: alta
sprint: S6
owner: por_definir

# ACT_0048 - Soporte de pegado y drag-drop de imagen en editor web

## Objetivo tecnico
Habilitar en el editor de items web la insercion de imagenes desde portapapeles y arrastrar/soltar, tanto en enunciado como en opciones.

## Tareas implementables
- [ ] Implementar captura de eventos `paste` y `drop` en los editores Tiptap del formulario de item.
- [ ] Detectar tipos de archivo de imagen soportados (`image/png`, `image/jpeg`, `image/webp`).
- [ ] Insertar nodo de imagen en el contenido del editor destino (enunciado o opcion correspondiente).
- [ ] Mostrar mensajes de error amigables para formatos no soportados.
- [ ] Verificar que no se rompa la edicion de texto en el flujo actual.

## Evidencias esperadas
- Insercion exitosa de imagen por `Ctrl+V` y por drag-drop.
- Persistencia del contenido enriquecido al crear/editar item.
- Registro visual de manejo de error en carga invalida.

## Criterio de terminado
El docente puede incluir imagenes desde portapapeles o arrastre en cualquier bloque editable del item sin interrumpir la funcionalidad existente.
