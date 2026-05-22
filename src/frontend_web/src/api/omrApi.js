import { API_BASE_URL } from './itemsApi';

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  return response.json();
}

async function requestJson(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  return response.json();
}

async function requestEmpty(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
}

export function listOmrAttempts({ teacherId, limit = 200, offset = 0 } = {}) {
  const query = new URLSearchParams();
  if (teacherId) query.append('teacher_id', teacherId);
  query.append('limit', String(limit));
  query.append('offset', String(offset));
  return request(`/omr/attempts?${query.toString()}`);
}

export function listOmrStudentAnswerReport({ teacherId, q } = {}) {
  const query = new URLSearchParams();
  if (teacherId) query.append('teacher_id', teacherId);
  if (q?.trim()) query.append('q', q.trim());
  return request(`/omr/student-answer-report?${query.toString()}`);
}

export function getOmrAttempt(attemptId) {
  return request(`/omr/attempts/${attemptId}`);
}

export function deleteOmrAttempt(attemptId) {
  return requestEmpty(`/omr/attempts/${attemptId}`, {
    method: 'DELETE',
  });
}

export function updateOmrAttemptAnswers(attemptId, answers) {
  return requestJson(`/omr/attempts/${attemptId}/answers`, {
    method: 'PATCH',
    body: JSON.stringify({ answers }),
  });
}

export function getOmrAttemptRatios(attemptId) {
  return request(`/omr/attempts/${attemptId}/ratios`);
}

export function getOmrAttemptOverlay(attemptId) {
  return request(`/omr/attempts/${attemptId}/overlay`);
}

export function assignOmrAttempt(attemptId, payload) {
  return requestJson(`/omr/attempts/${attemptId}/assign`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function getOmrThresholds() {
  return request('/omr/thresholds');
}

export function updateOmrThresholds(payload) {
  return requestJson('/omr/thresholds', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}
