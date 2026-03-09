function getCurriculumLabel(item) {
  const standard = item.curriculum?.standard_code || '';
  const competency = item.curriculum?.competency_code || '';
  return [standard, competency].filter(Boolean).join(' / ') || '-';
}

export default function ItemList({ items, selectedItemId, onSelect }) {
  return (
    <section className="card">
      <h3>Items ({items.length})</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Enunciado</th>
              <th>Area</th>
              <th>Dificultad</th>
              <th>Curricular</th>
              <th>Accion</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className={selectedItemId === item.id ? 'row-selected' : ''}>
                <td>{item.id}</td>
                <td>{item.statement}</td>
                <td>{item.subject || '-'}</td>
                <td>{item.difficulty || '-'}</td>
                <td>{getCurriculumLabel(item)}</td>
                <td>
                  <button type="button" onClick={() => onSelect(item.id)}>
                    Consultar / Editar
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
