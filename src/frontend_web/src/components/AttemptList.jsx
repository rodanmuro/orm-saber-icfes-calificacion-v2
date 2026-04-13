function toLocalDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function AttemptList({ attempts, onView, onViewImage }) {
  return (
    <section className="card">
      <h3>Examenes calificados ({attempts.length})</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID intento</th>
              <th>Examen</th>
              <th>Version</th>
              <th>Nombre examen</th>
              <th>Estudiante</th>
              <th>Grupo</th>
              <th>Estado</th>
              <th>Calificacion</th>
              <th>Fecha</th>
              <th>Accion</th>
            </tr>
          </thead>
          <tbody>
            {attempts.map((row) => (
              <tr key={row.attempt_id}>
                <td>{row.attempt_id}</td>
                <td>{row.exam_id || '-'}</td>
                <td>{row.exam_version_code || '-'}</td>
                <td>{row.exam_title || '-'}</td>
                <td>{row.student_name || '-'}</td>
                <td>{row.student_group || '-'}</td>
                <td>{row.status}</td>
                <td>{row.score_percent ?? '-'}</td>
                <td>{toLocalDate(row.created_at)}</td>
                <td className="col-action">
                  <button type="button" onClick={() => onView(row)}>
                    Ver
                  </button>
                  <button
                    type="button"
                    onClick={() => onViewImage(row)}
                    disabled={!row.uploaded_image_path}
                  >
                    Imagen
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
