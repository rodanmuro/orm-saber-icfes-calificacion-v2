# Frontend Expo (ACT_0013)

App movil minima para validar conectividad LAN entre celular y backend local.

## 1) Configurar URL del backend

Copiar `.env.example` a `.env` y ajustar la IP local de tu computador:

```bash
cp .env.example .env
```

Ejemplo de valor:

```env
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.10:8000/api/v1
```

## 2) Levantar backend en LAN

Desde `src/backend`:

```bash
../../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir .
```

## 3) Levantar app Expo

Desde `src/frontend`:

```bash
npm start
```

Abrir la app Expo Go en el celular y escanear QR.

## 4) Probar conectividad

- En la pantalla `OMR LAN Check`, revisar/editar la URL base.
- Pulsar `Probar conexión`.
- Éxito esperado: `Conexión exitosa` y payload con `status: "ok"`.

## Checklist LAN

- Celular y computador en la misma red WiFi.
- Backend levantado en `0.0.0.0:8000`.
- IP local correcta en la URL base.
- Puerto 8000 permitido por firewall/router local.

