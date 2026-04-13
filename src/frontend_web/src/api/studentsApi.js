import { API_BASE_URL } from './itemsApi';

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  return response.json();
}

export function listStudents({ limit = 200, offset = 0 } = {}) {
  return request(`/students?limit=${limit}&offset=${offset}`);
}
