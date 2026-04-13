export async function sendPhotoToOcr({
  endpointUrl,
  photoUri,
  metadataPath,
  teacherId,
  examId,
  examVersionId,
  pxPerMm = 10.0,
  robustMode = true,
  saveDebugArtifacts = true,
}) {
  const formData = new FormData();
  formData.append('photo', {
    uri: photoUri,
    name: 'photo.jpg',
    type: 'image/jpeg',
  });
  formData.append('metadata_path', metadataPath);
  formData.append('px_per_mm', String(pxPerMm));
  formData.append('robust_mode', String(robustMode));
  formData.append('save_debug_artifacts', String(saveDebugArtifacts));
  if (teacherId) {
    formData.append('teacher_id', String(teacherId));
  }
  if (examId) {
    formData.append('exam_id', String(examId));
  }
  if (examVersionId) {
    formData.append('exam_version_id', String(examVersionId));
  }

  const response = await fetch(endpointUrl, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
    },
    body: formData,
  });

  const raw = await response.text();
  let payload = null;
  try {
    payload = JSON.parse(raw);
  } catch (_) {
    payload = { raw };
  }

  return {
    ok: response.ok,
    statusCode: response.status,
    payload,
  };
}
