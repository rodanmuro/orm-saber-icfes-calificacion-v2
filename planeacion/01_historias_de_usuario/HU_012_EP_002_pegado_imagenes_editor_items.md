# HU_012 - Pegado de imagenes en editor de items (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Dependencia funcional: `HU_005_EP_002_banco_items_docente_web.md`

## Historia de usuario
**Como** docente  
**Quiero** pegar imagenes desde el portapapeles en el editor del enunciado y opciones  
**Para** construir preguntas usando material visual (por ejemplo, capturas de referencia) sin flujo manual externo.

## Criterios de aceptacion
1. El editor permite pegar imagenes (`Ctrl+V`) dentro del enunciado y dentro de cada opcion.
2. El editor permite tambien arrastrar/soltar imagenes al area editable.
3. La imagen queda visible en la previsualizacion y persistida en el contenido del item.
4. Si el formato no es soportado o falla la carga, se muestra un mensaje claro sin romper el formulario.
5. La creacion/edicion de items sigue funcionando para texto e imagen en una misma pregunta.

## Evidencia esperada
- Flujo funcional de pegado/drag-drop de imagen en frontend web.
- Persistencia correcta del contenido en backend.
- Pruebas manuales documentadas con casos exitosos y de error.

## Notas
- Esta HU prioriza productividad docente y elimina friccion al pasar contenido visual al banco de items.
