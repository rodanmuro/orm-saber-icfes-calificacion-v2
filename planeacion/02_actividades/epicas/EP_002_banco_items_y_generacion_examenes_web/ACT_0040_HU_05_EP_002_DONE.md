estado: done
prioridad: alta
sprint: S4
owner: por_definir

# ACT_0040 - Editor enriquecido de items (ecuaciones e imagenes)

## Objetivo tecnico
Extender el editor web de items para soportar contenido enriquecido con ecuaciones e imagenes en enunciado y opciones, manteniendo compatibilidad de persistencia en backend.

## Tareas implementables
- [x] Integrar Tiptap en campos de enunciado y opciones A/B/C/D.
- [x] Integrar soporte de ecuaciones (LaTeX) en el editor.
- [x] Integrar soporte de imagenes con carga a backend y URL de retorno.
- [x] Exponer endpoint backend para carga de imagenes del banco de items.
- [x] Validar guardado/lectura de contenido enriquecido en backend sin romper items existentes.

## Evidencias esperadas
- UI con editor enriquecido funcional en enunciado y opciones.
- Endpoint de upload de imagenes operativo.
- Evidencia de item guardado con ecuacion e imagen.

## Criterio de terminado
El docente puede crear/editar items con ecuaciones e imagenes desde frontend web y dichos contenidos persisten y se recuperan correctamente.

## Evidencia de cierre
- Editor Tiptap integrado en `src/frontend_web/src/components/ItemForm.jsx`.
- Soporte de ecuaciones y serializacion JSON en `src/frontend_web/src/editor/MathInline.jsx` y `src/frontend_web/src/utils/editorDoc.js`.
- Endpoint de carga de assets operativo desde backend y uso en frontend.
- Validacion manual realizada: crear, editar y reabrir items con texto, ecuaciones e imagenes sin perdida de contenido.
