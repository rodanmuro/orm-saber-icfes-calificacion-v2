export async function sendPhotoToOcr({
  endpointUrl,
  photoUri,
  metadataPath,
  markedThreshold = 0.26,
  unmarkedThreshold = 0.10,
  pxPerMm = 10.0,
}) {
  const formData = new FormData();
  formData.append('photo', {
    uri: photoUri,
    name: 'photo.jpg',
    type: 'image/jpeg',
  });
  formData.append('metadata_path', metadataPath);
  formData.append('marked_threshold', String(markedThreshold));
  formData.append('unmarked_threshold', String(unmarkedThreshold));
  formData.append('px_per_mm', String(pxPerMm));

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
