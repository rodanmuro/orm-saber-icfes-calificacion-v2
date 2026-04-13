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

async function requestBlob(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  return {
    blob: await response.blob(),
    contentDisposition: response.headers.get('content-disposition') || '',
  };
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export function listExams(teacherId) {
  const query = teacherId ? `?teacher_id=${teacherId}` : '';
  return request(`/exams${query}`);
}

export function createExam(payload) {
  return request('/exams', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getExam(examId) {
  return request(`/exams/${examId}`);
}

export function addItemToExam(examId, itemId, orderPosition = null) {
  return request(`/exams/${examId}/items`, {
    method: 'POST',
    body: JSON.stringify({ item_id: itemId, order_position: orderPosition }),
  });
}

export function removeItemFromExam(examId, itemId) {
  return request(`/exams/${examId}/items/${itemId}`, {
    method: 'DELETE',
  });
}

export function publishExamVersion(examId, payload) {
  return request(`/exams/${examId}/versions/publish`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listExamVersions(examId) {
  return request(`/exams/${examId}/versions`);
}

export function getExamVersion(examId, versionId) {
  return request(`/exams/${examId}/versions/${versionId}`);
}

export async function exportExamVersionPdf(examId, versionId, filenameFallback) {
  const { blob } = await requestBlob(`/exams/${examId}/versions/${versionId}/export/pdf`);
  downloadBlob(blob, filenameFallback || `exam_${examId}_version_${versionId}.pdf`);
}

export async function exportExamVersionDocx(examId, versionId, filenameFallback) {
  const { blob } = await requestBlob(`/exams/${examId}/versions/${versionId}/export/docx`);
  downloadBlob(blob, filenameFallback || `exam_${examId}_version_${versionId}.docx`);
}
