import { docHasMeaningfulContent, docToPlainText, storageToDoc } from '../utils/editorDoc';

function statementPreview(item) {
  const doc = storageToDoc(item.statement);
  const text = docToPlainText(doc);
  if (!text && docHasMeaningfulContent(doc)) return '[contenido no textual]';
  if (!text) return '-';
  return text.length > 90 ? `${text.slice(0, 90)}...` : text;
}

export default function ItemList({
  items,
  selectedItemId,
  onSelect,
  selectedItemIds = [],
  onToggleItemSelection,
  onToggleAllVisibleItems,
  onBulkDelete,
  onBulkForceDelete,
  isBulkDeleting = false,
}) {
  const selectedSet = new Set(selectedItemIds);
  const visibleIds = items.map((item) => item.id);
  const visibleSelectedCount = visibleIds.filter((id) => selectedSet.has(id)).length;
  const allVisibleSelected = visibleIds.length > 0 && visibleSelectedCount === visibleIds.length;

  return (
    <section className="card">
      <div className="item-list-header">
        <h3>Items ({items.length})</h3>
        <div className="item-list-actions">
          <button
            type="button"
            className="btn-danger"
            disabled={isBulkDeleting || visibleSelectedCount === 0}
            onClick={() => onBulkDelete?.(visibleIds.filter((id) => selectedSet.has(id)))}
          >
            {isBulkDeleting ? 'Borrando...' : `Borrar seleccionados (${visibleSelectedCount})`}
          </button>
          <button
            type="button"
            className="btn-danger force"
            disabled={isBulkDeleting || visibleSelectedCount === 0}
            onClick={() => onBulkForceDelete?.(visibleIds.filter((id) => selectedSet.has(id)))}
          >
            {isBulkDeleting ? 'Forzando...' : `Forzar borrado (${visibleSelectedCount})`}
          </button>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={allVisibleSelected}
                  onChange={(event) => onToggleAllVisibleItems?.(visibleIds, event.target.checked)}
                  aria-label="Seleccionar todos los items visibles"
                />
              </th>
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
                <td>
                  <input
                    type="checkbox"
                    checked={selectedSet.has(item.id)}
                    onChange={(event) => onToggleItemSelection?.(item.id, event.target.checked)}
                    aria-label={`Seleccionar item ${item.id}`}
                  />
                </td>
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
