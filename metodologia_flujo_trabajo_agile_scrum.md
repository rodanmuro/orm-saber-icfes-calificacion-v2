# Metodologia de Flujo de Trabajo Agile Scrum y Estructura de Planeacion

## 1. Objetivo
Establecer lineamientos estables para planear y ejecutar trabajo bajo enfoque Agile Scrum, con trazabilidad entre epicas, historias de usuario y actividades tecnicas, minimizando sobre-documentacion y renombrados innecesarios.

## 2. Estructura de carpetas de planeacion
Toda la planeacion se organiza dentro de `planeacion/` con este orden:

- `planeacion/00_epicas`
- `planeacion/01_historias_de_usuario`
- `planeacion/02_actividades`

Este orden refleja el flujo natural de trabajo:

1. Epicas.
2. Historias de usuario.
3. Actividades tecnicas.

## 3. Convenciones de nomenclatura

### 3.1 Epicas
Archivos en `planeacion/00_epicas`:

- `EP_000_nombre_epica.md`
- `EP_001_nombre_epica.md`
- etc.

Reglas:

1. `EP_XXX` es el identificador estable de la epica.
2. El numero no representa prioridad del sprint, solo identificacion y trazabilidad.

### 3.2 Historias de usuario
Archivos en `planeacion/01_historias_de_usuario`:

- `HU_000_EP_000_nombre_epica.md`
- `HU_001_EP_001_nombre_epica.md`
- etc.

Reglas:

1. `HU_XXX` identifica el documento de historias asociado a una epica.
2. `EP_XXX` dentro del nombre asegura trazabilidad directa a la epica.

### 3.3 Actividades
Carpetas por epica en `planeacion/02_actividades/epicas`:

- `planeacion/02_actividades/epicas/EP_000_nombre_epica/`

Archivos de actividades por historia:

- `ACT_0000_HU_01_EP_000.md`
- `ACT_0001_HU_02_EP_000.md`
- etc.

Reglas:

1. `ACT_XXXX` es consecutivo tecnico de actividades.
2. `HU_YY` referencia la historia especifica dentro de la epica.
3. `EP_XXX` referencia la epica propietaria.
4. No incluir titulos largos en el nombre del archivo de actividad; el contexto va dentro del contenido.
5. Cuando cambie el estado de la actividad, el archivo debe renombrarse agregando sufijo de estado al final.
6. Formato de estado en nombre: `ACT_XXXX_HU_YY_EP_XXX_ESTADO.md`.
7. Estados permitidos en nombre: `TODO`, `IN_PROGRESS`, `DONE`, `BLOCKED`.

Ejemplos:
- `ACT_0000_HU_01_EP_000_TODO.md`
- `ACT_0000_HU_01_EP_000_IN_PROGRESS.md`
- `ACT_0000_HU_01_EP_000_DONE.md`

## 4. Flujo de trabajo Scrum aplicado

1. Definir o ajustar epica en `00_epicas`.
2. Derivar historias de usuario de la epica en `01_historias_de_usuario`.
3. Seleccionar historias para sprint actual (Sprint Planning).
4. Crear actividades solo para historias que entran al sprint actual en `02_actividades`.
5. Ejecutar desarrollo, pruebas y seguimiento diario (Daily).
6. Cerrar sprint con review y retrospectiva.

## 5. Reglas para evitar sobre-documentacion

1. Solo detallar actividades de historias que entren al sprint actual.
2. Limite por historia activa:
- 1 archivo de HU (valor + criterios de aceptacion).
- 1 archivo de actividades (ejecucion tecnica).
3. Definicion de terminado documental: documentacion suficiente para ejecutar sin bloqueo, no documentacion exhaustiva.

## 6. Reglas de mantenimiento y cambios

1. Fuente de verdad por nivel:
- Epica: objetivo y alcance.
- HU: valor de negocio y criterios de aceptacion.
- Actividades: pasos tecnicos del sprint.
2. Si cambia una HU:
- Actualizar primero HU.
- Actualizar actividades impactadas.
- Actualizar epica solo si cambia alcance macro.
3. Evitar renombrados frecuentes de archivos; priorizar estabilidad de IDs (`EP`, `HU`, `ACT`).

## 7. Estado Scrum y priorizacion
El estado debe mantenerse en dos lugares: nombre del archivo de actividad y contenido interno.

### 7.1 Estado en nombre de archivo (obligatorio para actividades)
- Renombrar el archivo cuando cambie de estado (`TODO`, `IN_PROGRESS`, `DONE`, `BLOCKED`).
- Mantener el mismo identificador base (`ACT_XXXX_HU_YY_EP_XXX`) y cambiar solo el sufijo de estado.

### 7.2 Estado dentro del contenido (tambien obligatorio)
- Mantener campos de estado dentro del archivo para lectura rapida y trazabilidad historica.
- Campos sugeridos:

- `estado: todo | in_progress | done`
- `prioridad: alta | media | baja`
- `sprint: S1, S2, ...`
- `owner: nombre/responsable`

## 8. Lineamientos de redaccion tecnica para LLM (previo a implementacion)
Cuando una LLM redacte epicas, historias de usuario o actividades antes de codificar, debe priorizar contenido orientado a implementacion tecnica y codigo, no redaccion extensa.

### 8.1 Regla general
- Redactar para ejecutar, no para explicar en exceso.
- Cada punto debe derivar en un cambio concreto de codigo, estructura, configuracion o prueba.
- Evitar texto narrativo largo si no agrega decisiones tecnicas accionables.

### 8.2 Para epicas
- Describir alcance tecnico real (modulos, capas, contratos, integraciones).
- Incluir restricciones tecnicas verificables (ejemplo: procesamiento en backend, no OCR en MVP).
- Evitar objetivos abstractos sin impacto directo en implementacion.

### 8.3 Para historias de usuario
- Definir criterios de aceptacion que se puedan probar en codigo o ejecucion.
- Preferir criterios binarios y observables.
- Evitar criterios ambiguos como \"mejorar\" o \"optimizar\" sin metrica.

### 8.4 Para actividades
- Formular tareas como acciones tecnicas concretas: crear archivo, exponer endpoint, agregar test, definir schema, configurar entorno.
- Incluir entregables verificables por ruta de archivo o comando.
- Limitar actividades documentales a lo minimo necesario para implementar.

### 8.5 Formato recomendado de actividad tecnica
- Objetivo tecnico corto (1-2 lineas).
- Lista de tareas implementables (checklist operativo).
- Evidencias esperadas (`rutas de archivos`, `tests`, `comandos`).
- Criterio de terminado: artefacto ejecutable o validable.

### 8.6 Antipatrones a evitar
- Actividades centradas solo en redaccion de documentos sin produccion de codigo.
- Multiples documentos que repiten el mismo contenido sin nueva decision tecnica.
- Descripciones largas sin mencionar archivos, modulos o pruebas concretas.
- Criterios de aceptacion que no puedan comprobarse con evidencia objetiva.

## 9. Recomendaciones de evolucion

1. Mantener un `backlog.md` indice con enlaces a epicas, HU y actividades activas.
2. Usar IDs estables para trazabilidad, aunque cambie el titulo descriptivo.
3. Incorporar esta metodologia como base de un skill operativo del proyecto.

## 10. Resultado esperado
Con esta metodologia se obtiene:

1. Orden consistente de planeacion.
2. Menor riesgo de sobre-documentacion.
3. Mejor trazabilidad entre niveles de trabajo.
4. Menor friccion por renombrados y cambios de estructura.
5. Mejor alineacion con eventos Scrum y ejecucion incremental.
