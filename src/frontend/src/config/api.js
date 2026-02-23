const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

function normalizeBaseUrl(url) {
  return String(url || '').trim().replace(/\/+$/, '');
}

export function getApiBaseUrl() {
  const configured = normalizeBaseUrl(process.env.EXPO_PUBLIC_API_BASE_URL);
  return configured || DEFAULT_API_BASE_URL;
}

export function buildHealthUrl(baseUrl) {
  const base = normalizeBaseUrl(baseUrl);
  if (!base) {
    return '';
  }
  return `${base}/health`;
}

