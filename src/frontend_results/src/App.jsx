import { useMemo, useState } from 'react';
import { API_BASE_URL, authenticateStudent, buildAttemptPdfUrl } from './api/studentPortalApi';

function formatDate(value) {
  if (!value) return '-';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString();
}

export default function App() {
  const [email, setEmail] = useState('');
  const [documentNumber, setDocumentNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [session, setSession] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = await authenticateStudent({
        email: email.trim().toLowerCase(),
        document_number: documentNumber.trim(),
      });
      setSession(payload);
    } catch (err) {
      setSession(null);
      setError(err.message || 'No fue posible consultar resultados');
    } finally {
      setLoading(false);
    }
  }

  const attempts = useMemo(() => session?.attempts || [], [session]);

  return (
    <main className="page">
      <section className="card">
        <h1>Portal de resultados</h1>
        <p className="helper">
          Consulta individual de resultados. Ingrese correo institucional y numero de identidad.
        </p>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Correo institucional
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="estudiante@colegio.edu.co"
              required
            />
          </label>
          <label>
            Numero de identidad
            <input
              type="text"
              value={documentNumber}
              onChange={(e) => setDocumentNumber(e.target.value)}
              placeholder="Documento"
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Consultando...' : 'Consultar resultados'}
          </button>
        </form>
        <p className="helper">API: {API_BASE_URL}</p>
        {error ? <p className="error">{error}</p> : null}
      </section>

      {session ? (
        <section className="card">
          <h2>{session.student?.name}</h2>
          <p className="helper">
            Documento: {session.student?.document_number} | Grupo: {session.student?.group_name}
          </p>
          {attempts.length === 0 ? <p>No hay examenes calificados para este estudiante.</p> : null}
          {attempts.length > 0 ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Intento</th>
                    <th>Examen</th>
                    <th>Version</th>
                    <th>Puntaje</th>
                    <th>Correctas</th>
                    <th>Incorrectas</th>
                    <th>No marcadas</th>
                    <th>Fecha</th>
                    <th>PDF</th>
                  </tr>
                </thead>
                <tbody>
                  {attempts.map((row) => (
                    <tr key={row.attempt_id}>
                      <td>{row.attempt_id}</td>
                      <td>{row.exam_title || '-'}</td>
                      <td>{row.version_code || '-'}</td>
                      <td>{row.score_percent ?? '-'}</td>
                      <td>{row.correct_count ?? '-'}</td>
                      <td>{row.incorrect_count ?? '-'}</td>
                      <td>{row.blank_count ?? '-'}</td>
                      <td>{formatDate(row.created_at)}</td>
                      <td>
                        <a
                          className="btn-link"
                          href={buildAttemptPdfUrl({
                            attemptId: row.attempt_id,
                            email: email.trim().toLowerCase(),
                            documentNumber: documentNumber.trim(),
                          })}
                        >
                          Descargar
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
