export async function listExams({ baseUrl, teacherId } = {}) {
  const query = teacherId ? `?teacher_id=${teacherId}` : '';
  const response = await fetch(`${baseUrl}/exams${query}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  return response.json();
}

export async function listExamVersions({ baseUrl, examId }) {
  const response = await fetch(`${baseUrl}/exams/${examId}/versions`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  return response.json();
}
