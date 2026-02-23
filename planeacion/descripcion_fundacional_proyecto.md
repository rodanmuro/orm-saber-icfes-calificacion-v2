## Documento Fundacional — Sistema de Calificación Automática OMR con Captura Móvil

---

# 1. Descripción general del proyecto

El proyecto consiste en desarrollar un sistema de calificación automática de hojas físicas de respuestas mediante tecnología **OMR (Optical Mark Recognition)**, utilizando dispositivos móviles para capturar imágenes de las hojas y un backend centralizado en la nube para procesarlas, evaluarlas y almacenar resultados.

El objetivo principal es:

- Permitir que un docente capture con su celular una hoja de respuestas tipo examen.
- Detectar automáticamente las marcas realizadas por el estudiante.
- Identificar al estudiante mediante información estructurada.
- Calificar respuestas según la clave del examen.
- Registrar resultados en una base de datos central.

El sistema está diseñado para funcionar con hojas fotocopiables reutilizables, evitando la necesidad de imprimir hojas personalizadas.

---

# 2. Principios fundamentales del diseño

## 2.1 OMR como fuente primaria de verdad

El sistema adopta explícitamente el principio:

```
OMR = fuente primaria de verdad
Manuscrito = evidencia secundaria
```

Esto implica:

- Toda la automatización depende exclusivamente de marcas OMR.
- La escritura manual se utiliza únicamente para auditoría visual y resolución de conflictos.
- Los datos manuscritos no participan en el procesamiento automático.

---

## 2.2 Hoja fotocopiable y reutilizable

Restricción clave del diseño:

- La hoja debe poder imprimirse una vez y luego fotocopiarse.
- No se utilizarán QR personalizados para identificar estudiantes o exámenes.
- Toda identificación se realizará mediante burbujas OMR.

---

# 3. Identificación del estudiante

## 3.1 Datos capturados mediante OMR

La identificación del estudiante se basa exclusivamente en información estructurada capturada por OMR.

### Tipo de documento

Opciones soportadas:

- RC — Registro Civil
- TI — Tarjeta de Identidad
- CC — Cédula de Ciudadanía
- CE — Cédula de Extranjería
- PA — Pasaporte
- PPT — Permiso por Protección Temporal
- OTRO

### Número de documento

- Rejilla vertical de dígitos (0–9).
- Cada columna representa un dígito del número de documento.
- Se admite longitud variable (configurable por plantilla).

---

## 3.2 Consideración sobre cambios de documento

Se reconoce que en el contexto colombiano una persona puede transicionar entre documentos, por ejemplo:

```
RC → TI → CC
```

Por ello:

- El documento **NO** se utiliza como clave primaria interna.
- Se adopta un modelo de identidad basado en **UUID**.

---

## 3.3 Modelo de identidad en base de datos

### PERSONA

- `persona_id` (UUID) — clave primaria estable e inmutable.

### DOCUMENTO_PERSONA

- `tipo_documento`
- `numero_documento`
- `persona_id`
- `estado` (ACTIVO / HISTORICO)

Este modelo permite:

- múltiples documentos asociados a una misma persona,
- mantenimiento de historial de identidad,
- evitar colisiones entre documentos similares de distintos tipos.

---

# 4. Identificación del examen

Decisiones adoptadas:

- No utilizar códigos QR.
- Utilizar un **código de examen mediante burbujas OMR**.

Ventajas:

- Permite hojas reutilizables.
- Soporta múltiples versiones de examen con una misma plantilla base.
- Evita impresión personalizada.

---

# 5. Información manuscrita

La hoja incluirá campos de escritura manuscrita:

- Nombre completo.
- Número de documento.
- Grupo.

Uso previsto:

- Auditoría visual.
- Validación humana.
- Recuperación ante errores de lectura OMR.

La información manuscrita **no se procesa mediante OCR** en la fase inicial del proyecto.

---

# 6. Diseño físico de la hoja

## 6.1 Tamaño

- Formato: **hoja tamaño carta**.

---

## 6.2 Marcadores de alineación

Se utilizarán **ArUco markers** para registro geométrico.

Características:

- 4 marcadores ArUco.
- Uno en cada esquina de la hoja.
- No colocados al borde (margen aproximado de 10–15 mm).

Funciones:

- Detección de orientación.
- Cálculo de homografía.
- Normalización de perspectiva.
- Estabilización del proceso OMR en fotografías móviles.

---

# 7. Arquitectura general del sistema

## 7.1 Enfoque cloud-first

El sistema adopta un enfoque **cloud-first** (calificación en backend).

Responsabilidades del celular:

- Captura de imagen.
- Validación visual mediante overlay.
- Compresión de la imagen.
- Envío de la imagen a la API.

Responsabilidades del backend:

- Detección ArUco.
- Corrección de perspectiva (homografía).
- Lectura OMR por ROIs.
- Identificación del estudiante y del examen.
- Calificación.
- Persistencia de datos y evidencias.

---

## 7.2 Flujo operativo

1. El docente abre la aplicación móvil.
2. Un overlay guía el posicionamiento de la hoja.
3. Se realiza la captura manual (incremento inicial).
4. La imagen se comprime y se envía a la API.
5. El backend ejecuta:
   - detección de ArUco,
   - corrección de perspectiva,
   - lectura de ROIs OMR,
   - identificación del estudiante,
   - identificación del examen,
   - calificación de respuestas,
   - almacenamiento de resultados.
6. La API responde con la calificación y metadatos.

---

# 8. Arquitectura tecnológica

## 8.1 Frontend móvil

Stack definido:

- Flutter.
- Acceso a cámara nativa.
- Overlay visual para guía de captura.

Estrategia incremental:

- MVP: captura manual.
- Evolución: detección ArUco en vivo y auto-disparo mediante OpenCV nativo (módulo nativo; el procesamiento OMR sigue en backend).

---

## 8.2 Backend

Stack definido:

- Python.
- FastAPI.
- OpenCV (incluyendo módulo ArUco).
- Motor OMR basado conceptualmente en OMRChecker.

Persistencia:

- PostgreSQL para datos estructurados.
- Almacenamiento S3-compatible / MinIO para imágenes y evidencias.

---

# 9. Generación de plantillas (módulo fundacional)

## 9.1 Principio

La plantilla no se diseña manualmente en Word/Paint. Se define mediante un layout matemático y se genera programáticamente para garantizar precisión y repetibilidad.

Regla:

- `template.json` (coordenadas/ROIs) es la fuente de verdad.
- El PDF es una representación visual generada desde esas coordenadas.

## 9.2 Salidas del generador

El módulo de plantillas (backend) debe producir:

- Un PDF imprimible en tamaño carta con:
  - 4 ArUco markers,
  - campos manuscritos,
  - bloques OMR (tipo_doc, número_doc, código examen, respuestas).
- Un `template.json` asociado, con coordenadas exactas para lectura OMR por ROIs.

## 9.3 Tecnología del generador

Se utilizará un generador en Python basado en:

- **ReportLab** (generación de PDF con precisión geométrica).
- OpenCV (opcional) para generar/validar imágenes de ArUco antes de incrustarlas en el PDF.

## 9.4 Prioridad de desarrollo

Este módulo de generación de plantillas es el **primer incremento técnico** a implementar, ya que fija el layout y las coordenadas que el motor OMR usará para calificar.

---

# 10. Librerías OMR evaluadas

Se evaluaron las siguientes alternativas:

- OMRChecker.
- OpenMCR.
- FormReturn.

Decisión adoptada:

- **OMRChecker** es la base conceptual más alineada con el proyecto.
- Se utilizará como referencia para el motor OMR.
- Su pipeline se adaptará para usar ArUco como mecanismo de alineación.

---

# 11. Estrategia de incrementos

## Incremento 1 — MVP funcional

- Generador de plantilla (PDF + template.json) con ReportLab.
- Overlay de captura en Flutter.
- Disparo manual.
- Backend OMR operativo (ArUco + warp + lectura de ROIs + calificación).
- Respuesta JSON de calificación.

## Incremento 2 — Mejora de experiencia

- Detección ArUco en tiempo real en el móvil.
- Auto-disparo cuando se detecten los 4 marcadores.
- Validaciones de estabilidad y nitidez en captura.

---

# 12. Objetivos técnicos clave

- Alta precisión usando fotografías (no escáner).
- Robustez frente a fotocopias y variabilidad de impresión.
- Baja latencia operativa en flujo secuencial.
- Arquitectura escalable y mantenible.
- Separación estricta entre captura móvil y procesamiento en servidor.
- Plantillas generadas programáticamente y versionadas.

---

Este documento constituye la base conceptual, técnica y arquitectónica del sistema y servirá como referencia para futuras decisiones de diseño e implementación.