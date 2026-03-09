const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }

  return response.json();
}

export function listItems() {
  return request('/items');
}

export function getItem(itemId) {
  return request(`/items/${itemId}`);
}

export function createItem(payload) {
  return request('/items', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateItem(itemId, payload) {
  return request(`/items/${itemId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export { API_BASE_URL };
