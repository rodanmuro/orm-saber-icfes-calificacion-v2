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

export async function deleteItem(itemId) {
  const response = await fetch(`${API_BASE_URL}/items/${itemId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
}

export function listCurriculumStandards(query = '') {
  const params = new URLSearchParams();
  if (query?.trim()) params.set('q', query.trim());
  params.set('limit', '20');
  return request(`/curriculum/standards?${params.toString()}`);
}

export function listCurriculumCompetencies({ standardId = null, query = '' } = {}) {
  const params = new URLSearchParams();
  if (standardId) params.set('standard_id', String(standardId));
  if (query?.trim()) params.set('q', query.trim());
  params.set('limit', '20');
  return request(`/curriculum/competencies?${params.toString()}`);
}

export function generateItemAIDraft(payload) {
  return request('/ai/generate-item', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export { API_BASE_URL };
