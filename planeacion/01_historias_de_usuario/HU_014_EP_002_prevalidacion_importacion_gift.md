# HU_014 - Prevalidacion y confirmacion antes de importar GIFT (EP_002)

## Trazabilidad
- Epica asociada: `EP_002_banco_items_y_generacion_examenes_web.md`
- Dependencias: HU_013 completada o parcialmente disponible.

## Historia de usuario
**Como** docente  
**Quiero** previsualizar y validar los items detectados en un archivo GIFT antes de guardarlos  
**Para** evitar importar preguntas incompletas o con errores al banco principal.

## Criterios de aceptacion
1. El sistema presenta una vista previa de items validos e items con error antes de persistir.
2. El docente puede confirmar la importacion solo de items validos.
3. La validacion incluye campos minimos: enunciado, 4 opciones y respuesta correcta.
4. Los errores quedan reportados con razon legible para correccion.
5. La confirmacion genera un resumen final de importados/omitidos.

## Evidencia esperada
- Flujo en dos pasos: analizar archivo y confirmar importacion.
- Registro de errores por item.
- Pruebas de aceptacion con mezcla de items validos e invalidos.

## Notas
- Esta HU reduce riesgo de contaminacion del banco y mejora control de calidad previo a persistencia.
