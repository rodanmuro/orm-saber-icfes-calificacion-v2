# EP_000 - Generador de plantilla basica OMR con ArUco

## Objetivo tecnico
Implementar un modulo que genere una plantilla basica OMR en formato carta, con marcadores ArUco para alineacion y un bloque rectangular con burbujas definidas de forma parametrizable.

## Alcance
- Generar plantilla visual en formato carta.
- Incluir 4 marcadores ArUco (uno por esquina) con margenes de seguridad.
- Incluir un area rectangular principal para lectura OMR.
- Incluir una serie inicial de burbujas OMR con layout fijo configurable por parametros.
- Generar una salida estructurada de coordenadas de referencia para cada burbuja.

## Fuera de alcance
- Calificacion de respuestas.
- Integracion con backend/API.
- Captura movil en tiempo real.
- OCR de campos manuscritos.

## Entregables verificables
- Modulo de generacion de plantilla en `src/`.
- Archivo de salida visual de plantilla (PDF o imagen segun decision tecnica).
- Archivo de metadatos de plantilla (por ejemplo `template.json`) con:
  - dimensiones de pagina,
  - ubicacion de ArUco,
  - bounding boxes/centros/radios de burbujas,
  - identificadores de burbujas.
- Script o comando reproducible para regenerar la plantilla.

## Restricciones tecnicas
- Coordenadas deterministicas y repetibles.
- ArUco siempre dentro del area imprimible con margen explicito.
- Definicion geometrica como fuente de verdad para layout.

## Criterios de aceptacion
1. La plantilla generada incluye exactamente 4 marcadores ArUco detectables y ubicados en las cuatro esquinas logicas.
2. Existe un bloque rectangular principal visible que contiene todas las burbujas definidas.
3. Cada burbuja visible tiene correspondencia 1:1 en el archivo de metadatos.
4. Ejecutar nuevamente el generador produce geometria consistente (sin cambios no intencionales de coordenadas).
5. El comando de generacion queda documentado y es ejecutable en entorno local.
