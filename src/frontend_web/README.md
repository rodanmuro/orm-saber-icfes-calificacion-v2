# Frontend Web - Banco de Items

Frontend web base para gestion de items (HU_005 / ACT_0033).

## Requisitos
- Node.js 18+
- Backend FastAPI corriendo en `http://localhost:8000`

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
