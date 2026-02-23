export async function checkHealth(healthUrl) {
  const response = await fetch(healthUrl, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
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

