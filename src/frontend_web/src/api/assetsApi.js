import { API_BASE_URL } from './itemsApi';

const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1$/, '');

export function resolveAssetUrl(url) {
  if (!url) return '';
  if (!url.startsWith('http')) {
    return `${API_ORIGIN}${url}`;
  }

  try {
    const parsed = new URL(url);
    const isLocalHost =
      parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1';
    if (isLocalHost) {
      // Reescribe urls antiguas (ej. :8000) al backend actual configurado.
      return `${API_ORIGIN}${parsed.pathname}${parsed.search}${parsed.hash}`;
    }
  } catch {
    return url;
  }
  return url;
}

export async function uploadEditorImage(file) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch(`${API_BASE_URL}/assets/images`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }

  const payload = await response.json();
  const absolute = resolveAssetUrl(payload.url || '');

  return {
    ...payload,
    absoluteUrl: absolute,
  };
}
