function resolveApiBaseUrl() {
  const configured = String(import.meta.env.VITE_API_BASE_URL || '').trim();
  if (configured) {
    try {
      const parsed = new URL(configured);
      if (
        typeof window !== 'undefined' &&
        window.location.hostname &&
        !['localhost', '127.0.0.1'].includes(window.location.hostname) &&
        ['localhost', '127.0.0.1'].includes(parsed.hostname)
      ) {
        parsed.hostname = window.location.hostname;
      }
      return parsed.toString().replace(/\/+$/, '');
    } catch {
      return configured.replace(/\/+$/, '');
    }
  }
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol || 'http:';
    const host = window.location.hostname || 'localhost';
    return `${protocol}//${host}:8001/api/v1`;
  }
  return 'http://localhost:8001/api/v1';
}

const API_BASE_URL = resolveApiBaseUrl();

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      if (payload?.detail) detail = payload.detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return response.json();
}

export function authenticateStudent({ email, document_number }) {
  return requestJson('/student-portal/authenticate', {
    method: 'POST',
    body: JSON.stringify({ email, document_number }),
  });
}

export function buildAttemptPdfUrl({ attemptId, email, documentNumber }) {
  const params = new URLSearchParams({
    email: String(email || ''),
    document_number: String(documentNumber || ''),
  });
  return `${API_BASE_URL}/student-portal/attempts/${attemptId}/export/pdf?${params.toString()}`;
}

export { API_BASE_URL };
