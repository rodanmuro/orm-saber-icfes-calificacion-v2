# Frontend Web - Banco de Items

Frontend web base para gestion de items (HU_005 / ACT_0033).

## Requisitos
- Node.js 18+
- Backend FastAPI corriendo en `http://localhost:8001`

## Configuracion
1. Copiar variables de entorno:
   - `cp .env.example .env.local`
2. Ajustar `VITE_API_BASE_URL` si aplica.

## Ejecucion
```bash
npm install
npm run dev
```

## Flujo soportado
- Crear item (`POST /api/v1/items`)
- Listar items (`GET /api/v1/items`)
- Consultar item (`GET /api/v1/items/{id}`)
- Editar item (`PUT /api/v1/items/{id}`)
- Filtros basicos en cliente por area, dificultad y etiqueta curricular.
- Crear examen (`POST /api/v1/exams`)
- Listar examenes por docente (`GET /api/v1/exams?teacher_id=...`)
- Consultar examen con items asociados (`GET /api/v1/exams/{id}`)
- Asociar item a examen (`POST /api/v1/exams/{id}/items`)
- Desasociar item de examen (`DELETE /api/v1/exams/{id}/items/{item_id}`)

## Editor de contenido
- El enunciado y las opciones A/B/C/D usan Tiptap.
- Soporte de ecuaciones: boton `fx` para insertar LaTeX.
- Soporte de imagenes: boton `Imagen` con upload al backend (`POST /api/v1/assets/images`).
- El frontend serializa el contenido del editor en JSON (string) para mantener compatibilidad con el backend actual.
