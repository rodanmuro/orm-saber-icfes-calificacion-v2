import { useMemo, useState } from 'react';
import { storageToDoc } from '../utils/editorDoc';
import RichDocPreview from './RichDocPreview';

function formatDecimal(value, digits = 2) {
  if (value == null || Number.isNaN(Number(value))) return '-';
  return Number(value).toFixed(digits);
}

export default function AnalyticsPanel({
  attempts,
  items,
  filters,
  examCodeOptions,
  groupOptions,
  loading,
  summary,
  questionStats,
  onFilterChange,
  onRefresh,
}) {
  const [sortBy, setSortBy] = useState('questionNumber');
  const [sortDir, setSortDir] = useState('asc');
  const [previewRow, setPreviewRow] = useState(null);
  const [markedModalRow, setMarkedModalRow] = useState(null);

  const hasData = attempts.length > 0;
  const itemsById = useMemo(() => {
    const map = new Map();
    (items || []).forEach((item) => map.set(item.id, item));
    return map;
  }, [items]);

  const sortedQuestionRows = useMemo(() => {
    const rows = [...questionStats];
    rows.sort((a, b) => {
      const av = a?.[sortBy];
      const bv = b?.[sortBy];
      if (typeof av === 'number' && typeof bv === 'number') {
        return sortDir === 'asc' ? av - bv : bv - av;
      }
      const as = String(av ?? '');
      const bs = String(bv ?? '');
      return sortDir === 'asc' ? as.localeCompare(bs) : bs.localeCompare(as);
    });
    return rows;
  }, [questionStats, sortBy, sortDir]);

  const chartRows = useMemo(
    () => [...sortedQuestionRows].sort((a, b) => b.incorrect - a.incorrect).slice(0, 12),
    [sortedQuestionRows],
  );

  function toggleSort(key) {
    if (sortBy === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
      return;
    }
    setSortBy(key);
    setSortDir(key === 'questionNumber' || key === 'itemId' ? 'asc' : 'desc');
  }

  function sortMark(key) {
    if (sortBy !== key) return '';
    return sortDir === 'asc' ? ' ↑' : ' ↓';
  }

  function openPreview(row) {
    if (!row?.itemId) return;
    setPreviewRow(row);
  }

  function openMarkedModal(row) {
    setMarkedModalRow(row);
  }

  const previewItem = previewRow?.itemId ? itemsById.get(previewRow.itemId) : null;

  return (
    <section className="card">
      <h3>Analiticas</h3>
      <div className="filters-grid">
        <label>
          Codigo examen
          <select
            value={filters.examCode}
            onChange={(event) => onFilterChange({ ...filters, examCode: event.target.value })}
          >
            <option value="">Todos</option>
            {examCodeOptions.map((code) => (
              <option key={code} value={code}>{code}</option>
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
            {groupOptions.map((group) => (
              <option key={group} value={group}>{group}</option>
            ))}
          </select>
        </label>
        <label>
          <span>&nbsp;</span>
          <button type="button" onClick={onRefresh} disabled={loading}>
            {loading ? 'Calculando...' : 'Recalcular'}
          </button>
        </label>
      </div>

      <div className="analytics-summary-grid">
        <div className="analytics-card">
          <span className="analytics-label">Intentos analizados</span>
          <strong>{summary.attemptCount}</strong>
        </div>
        <div className="analytics-card">
          <span className="analytics-label">Promedio puntuacion</span>
          <strong>{formatDecimal(summary.avgScorePercent)}%</strong>
        </div>
        <div className="analytics-card">
          <span className="analytics-label">Preguntas con datos</span>
          <strong>{summary.questionCount}</strong>
        </div>
      </div>

      {!hasData ? <p>No hay intentos para analizar con los filtros actuales.</p> : null}

      {hasData ? (
        <>
          <h4>Grafica de barras (errores por pregunta)</h4>
          <div className="analytics-bars">
            {chartRows.map((row) => {
              const max = Math.max(...chartRows.map((entry) => entry.incorrect || 0), 1);
              const width = Math.max(4, Math.round(((row.incorrect || 0) / max) * 100));
              return (
                <div className="analytics-bar-row" key={`bar-${row.questionNumber}`}>
                  <span className="analytics-bar-label">P{row.questionNumber}</span>
                  <div className="analytics-bar-track">
                    <div className="analytics-bar-fill" style={{ width: `${width}%` }} />
                  </div>
                  <span className="analytics-bar-value">{row.incorrect}</span>
                </div>
              );
            })}
          </div>

          <h4>Resultados por pregunta</h4>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('questionNumber')}>
                    Pregunta{sortMark('questionNumber')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('itemId')}>
                    ID item{sortMark('itemId')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('correct')}>
                    Bien{sortMark('correct')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('incorrect')}>
                    Mal{sortMark('incorrect')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('answered')}>
                    Respondidas{sortMark('answered')}
                  </button>
                </th>
                <th>Marcadas</th>
                <th>Ver</th>
              </tr>
            </thead>
            <tbody>
              {sortedQuestionRows.map((row) => (
                <tr key={row.questionNumber}>
                  <td>{row.questionNumber}</td>
                  <td>{row.itemId || '-'}</td>
                  <td>{row.correct}</td>
                  <td>{row.incorrect}</td>
                  <td>{row.answered}</td>
                  <td>
                    <button type="button" onClick={() => openMarkedModal(row)}>
                      Ver
                    </button>
                  </td>
                  <td>
                    <button
                      type="button"
                      onClick={() => openPreview(row)}
                      disabled={!row.itemId || !itemsById.get(row.itemId)}
                    >
                      Ver
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
      ) : null}

      {markedModalRow ? (
        <div className="preview-modal-overlay" onClick={() => setMarkedModalRow(null)}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Distribucion de marcadas | Pregunta {markedModalRow.questionNumber}</h4>
              <button type="button" onClick={() => setMarkedModalRow(null)}>Cerrar</button>
            </div>
            <p className="helper-text">Total respuestas: {markedModalRow.markedTotal || 0}</p>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Opcion</th>
                    <th>Cantidad</th>
                    <th>%</th>
                  </tr>
                </thead>
                <tbody>
                  {['A', 'B', 'C', 'D', 'blank', 'ambiguous'].map((key) => {
                    const count = Number(markedModalRow.markedDistribution?.[key] || 0);
                    const total = Number(markedModalRow.markedTotal || 0);
                    const pct = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
                    return (
                      <tr key={key}>
                        <td>{key === 'blank' ? 'No marcada' : key === 'ambiguous' ? 'Ambigua' : key}</td>
                        <td>{count}</td>
                        <td>{pct}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}

      {previewRow ? (
        <div className="preview-modal-overlay" onClick={() => setPreviewRow(null)}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Pregunta {previewRow.questionNumber} | Item #{previewRow.itemId || '-'}</h4>
              <button type="button" onClick={() => setPreviewRow(null)}>Cerrar</button>
            </div>
            {previewItem ? (
              <>
                <div className="preview-modal-section">
                  <h5>Enunciado</h5>
                  <RichDocPreview value={storageToDoc(previewItem.statement)} />
                </div>
                <div className="preview-modal-options">
                  <div className="preview-modal-section">
                    <h5>Opcion A</h5>
                    <RichDocPreview value={storageToDoc(previewItem.options?.A)} />
                  </div>
                  <div className="preview-modal-section">
                    <h5>Opcion B</h5>
                    <RichDocPreview value={storageToDoc(previewItem.options?.B)} />
                  </div>
                  <div className="preview-modal-section">
                    <h5>Opcion C</h5>
                    <RichDocPreview value={storageToDoc(previewItem.options?.C)} />
                  </div>
                  <div className="preview-modal-section">
                    <h5>Opcion D</h5>
                    <RichDocPreview value={storageToDoc(previewItem.options?.D)} />
                  </div>
                </div>
              </>
            ) : (
              <p>No se encontro el item en el listado cargado.</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
