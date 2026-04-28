function toLocalDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function AttemptList({
  attempts,
  filters,
  statusOptions,
  groupOptions,
  thresholds,
  savingThresholds,
  onFilterChange,
  onThresholdChange,
  onThresholdBlur,
  onView,
  onViewImage,
  onViewRatios,
  onViewOverlay,
  selectedAttemptIds,
  deletingAttemptIds,
  deletingSelected,
  onToggleAttemptSelection,
  onToggleAllAttempts,
  onDelete,
  onDeleteSelected,
}) {
  const selectedCount = selectedAttemptIds.length;
  const allVisibleSelected = attempts.length > 0 && attempts.every((row) => selectedAttemptIds.includes(row.attempt_id));

  return (
    <section className="card">
      <h3>Examenes calificados ({attempts.length})</h3>
      <div className="filters-grid">
        <label>
          Buscar
          <input
            type="text"
            placeholder="Examen, estudiante, version..."
            value={filters.query}
            onChange={(event) => onFilterChange({ ...filters, query: event.target.value })}
          />
        </label>
        <label>
          Estado
          <select
            value={filters.status}
            onChange={(event) => onFilterChange({ ...filters, status: event.target.value })}
          >
            <option value="">Todos</option>
            {statusOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          Grupo
          <select
            value={filters.group}
            onChange={(event) => onFilterChange({ ...filters, group: event.target.value })}
          >
            <option value="">Todos</option>
            {groupOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          Umbral marcada
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={thresholds.marked}
            onChange={(event) => onThresholdChange('marked', event.target.value)}
            onBlur={onThresholdBlur}
          />
        </label>
        <label>
          Umbral no marcada
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={thresholds.unmarked}
            onChange={(event) => onThresholdChange('unmarked', event.target.value)}
            onBlur={onThresholdBlur}
          />
        </label>
      </div>
      <p className="helper-text">
        Los nuevos umbrales aplican a lecturas futuras. {savingThresholds ? 'Guardando...' : ''}
      </p>
      <div className="attempt-bulk-actions">
        <span>{selectedCount} seleccionado{selectedCount === 1 ? '' : 's'}</span>
        <button
          type="button"
          className="btn-danger"
          onClick={onDeleteSelected}
          disabled={selectedCount === 0 || deletingSelected}
        >
          {deletingSelected ? 'Borrando...' : 'Borrar seleccionados'}
        </button>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th className="col-select">
                <input
                  type="checkbox"
                  aria-label="Seleccionar intentos visibles"
                  checked={allVisibleSelected}
                  disabled={attempts.length === 0}
                  onChange={(event) => onToggleAllAttempts(event.target.checked)}
                />
              </th>
              <th>ID intento</th>
              <th>Examen</th>
              <th>Version</th>
              <th>Nombre examen</th>
              <th>Estudiante</th>
              <th>Grupo</th>
              <th>Estado</th>
              <th>Total</th>
              <th>Correctas</th>
              <th>Incorrectas</th>
              <th>No marcadas</th>
              <th>Calificacion</th>
              <th>Fecha</th>
              <th>Accion</th>
            </tr>
          </thead>
          <tbody>
            {attempts.map((row) => {
              const isDeleting = deletingAttemptIds.includes(row.attempt_id);
              return (
              <tr key={row.attempt_id} className={row.status === 'needs_review' ? 'row-needs-review' : undefined}>
                <td className="col-select">
                  <input
                    type="checkbox"
                    aria-label={`Seleccionar intento ${row.attempt_id}`}
                    checked={selectedAttemptIds.includes(row.attempt_id)}
                    disabled={isDeleting || deletingSelected}
                    onChange={(event) => onToggleAttemptSelection(row.attempt_id, event.target.checked)}
                  />
                </td>
                <td>{row.attempt_id}</td>
                <td>{row.exam_id || '-'}</td>
                <td>{row.exam_version_code || '-'}</td>
                <td>{row.exam_title || '-'}</td>
                <td>{row.student_name || '-'}</td>
                <td>{row.student_group || '-'}</td>
                <td>{row.status}</td>
                <td>{row.total_questions ?? '-'}</td>
                <td>{row.correct_count ?? '-'}</td>
                <td>{row.incorrect_count ?? '-'}</td>
                <td>{row.blank_count ?? '-'}</td>
                <td>{row.score_percent ?? '-'}</td>
                <td>{toLocalDate(row.created_at)}</td>
                <td className="col-action">
                  <button type="button" onClick={() => onView(row)}>
                    Ver
                  </button>
                  <button type="button" onClick={() => onViewRatios(row)}>
                    Ratios
                  </button>
                  <button type="button" onClick={() => onViewOverlay(row)}>
                    Overlay
                  </button>
                  <button
                    type="button"
                    onClick={() => onViewImage(row)}
                    disabled={!row.uploaded_image_path}
                  >
                    Imagen
                  </button>
                  <button
                    type="button"
                    className="btn-danger"
                    onClick={() => onDelete(row)}
                    disabled={isDeleting || deletingSelected}
                  >
                    {isDeleting ? 'Borrando...' : 'Borrar'}
                  </button>
                </td>
              </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
