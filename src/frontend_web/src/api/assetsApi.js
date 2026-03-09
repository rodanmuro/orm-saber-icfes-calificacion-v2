import { API_BASE_URL } from './itemsApi';

const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1$/, '');

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
  const relative = payload.url || '';
  const absolute = relative.startsWith('http') ? relative : `${API_ORIGIN}${relative}`;

  return {
    ...payload,
    absoluteUrl: absolute,
  };
}
