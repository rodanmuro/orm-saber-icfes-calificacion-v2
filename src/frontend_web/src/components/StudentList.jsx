function applyFilters(students, filters) {
  const query = (filters.query || '').trim().toLowerCase();
  const group = (filters.group || '').trim().toLowerCase();
  if (!query && !group) return students;

  return students.filter((student) => {
    if (group && !(student.group_name || '').toLowerCase().includes(group)) return false;
    if (!query) return true;
    const haystack = [
      student.first_name,
      student.last_name,
      student.email,
      student.document_number,
      student.external_uuid,
      student.group_name,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(query);
  });
}

function applySort(students, sortKey) {
  const sorted = [...students];
  const asc = (a, b) => (a > b ? 1 : a < b ? -1 : 0);
  switch (sortKey) {
    case 'id_desc':
      return sorted.sort((a, b) => b.id - a.id);
    case 'apellido_asc':
      return sorted.sort((a, b) => asc(a.last_name, b.last_name) || asc(a.first_name, b.first_name));
    case 'apellido_desc':
      return sorted.sort((a, b) => asc(b.last_name, a.last_name) || asc(b.first_name, a.first_name));
    case 'grupo_asc':
      return sorted.sort((a, b) => asc(a.group_name, b.group_name) || asc(a.last_name, b.last_name));
    case 'grupo_desc':
      return sorted.sort((a, b) => asc(b.group_name, a.group_name) || asc(a.last_name, b.last_name));
    case 'documento_asc':
      return sorted.sort((a, b) => asc(a.document_number, b.document_number));
    case 'documento_desc':
      return sorted.sort((a, b) => asc(b.document_number, a.document_number));
    default:
      return sorted.sort((a, b) => a.id - b.id);
  }
}

export default function StudentList({ students, filters, sortKey }) {
  const filtered = applyFilters(students, filters);
  const sorted = applySort(filtered, sortKey);
  return (
    <section className="card">
      <h3>Estudiantes ({sorted.length})</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Documento</th>
              <th>Nombre</th>
              <th>Apellido</th>
              <th>Correo</th>
              <th>Grupo</th>
              <th>UUID</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((student) => (
              <tr key={student.id}>
                <td>{student.id}</td>
                <td>{student.document_type} {student.document_number}</td>
                <td>{student.first_name}</td>
                <td>{student.last_name}</td>
                <td>{student.email || '-'}</td>
                <td>{student.group_name}</td>
                <td className="cell-truncate" title={student.external_uuid}>
                  {student.external_uuid}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
