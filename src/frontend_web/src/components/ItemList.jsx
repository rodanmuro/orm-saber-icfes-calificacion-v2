import { docHasMeaningfulContent, docToPlainText, storageToDoc } from '../utils/editorDoc';

function statementPreview(item) {
  const doc = storageToDoc(item.statement);
  const text = docToPlainText(doc);
  if (!text && docHasMeaningfulContent(doc)) return '[contenido no textual]';
  if (!text) return '-';
  return text.length > 90 ? `${text.slice(0, 90)}...` : text;
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
              <th>Estandar</th>
              <th>Competencia</th>
              <th>Accion</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className={selectedItemId === item.id ? 'row-selected' : ''}>
                <td>{item.id}</td>
                <td>{statementPreview(item)}</td>
                <td>{item.subject || '-'}</td>
                <td>{item.difficulty || '-'}</td>
                <td>{item.curriculum?.standard_name || '-'}</td>
                <td>{item.curriculum?.competency_name || '-'}</td>
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
