# HU_013 - Importacion masiva de items desde GIFT (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Dependencia funcional: `HU_005_EP_002_banco_items_docente_web.md`

## Historia de usuario
**Como** docente  
**Quiero** importar preguntas de seleccion multiple desde archivos GIFT  
**Para** poblar rapidamente el banco de items desde material ya existente (por ejemplo Moodle).

## Criterios de aceptacion
1. El sistema permite cargar un archivo `.gift` desde la interfaz web.
2. El backend parsea preguntas de opcion multiple y extrae enunciado, opciones y respuesta correcta.
3. Los items importados se guardan asociados al docente que realiza la carga.
4. Los errores de sintaxis se reportan por item/linea sin abortar silenciosamente.
5. El resultado de importacion informa total procesado, total importado y total con error.

## Evidencia esperada
- Endpoint/backend de importacion GIFT funcionando.
- Flujo frontend para subir archivo y mostrar resultado.
- Pruebas con archivos GIFT validos e invalidos.

## Notas
- El alcance inicial cubre GIFT de seleccion multiple; variantes complejas se atienden incrementalmente.
