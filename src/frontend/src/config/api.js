const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
const DEFAULT_METADATA_PATH = 'data/output/template_basica_omr_v1.json';

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

export function buildOcrReadUrl(baseUrl) {
  const base = normalizeBaseUrl(baseUrl);
  if (!base) {
    return '';
  }
  return `${base}/omr/read-photo`;
}

export function getDefaultMetadataPath() {
  const configured = String(process.env.EXPO_PUBLIC_METADATA_PATH || '').trim();
  return configured || DEFAULT_METADATA_PATH;
}
