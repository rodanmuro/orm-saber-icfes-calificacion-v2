import { API_BASE_URL } from './itemsApi';

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

export function listAnonymousExams(teacherId) {
  const query = teacherId ? `?teacher_id=${teacherId}` : '';
  return request(`/anonymous-exams${query}`);
}

export function createAnonymousExam(payload) {
  return request('/anonymous-exams', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
