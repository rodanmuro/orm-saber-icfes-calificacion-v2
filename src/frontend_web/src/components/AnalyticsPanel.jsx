import { useMemo, useState } from 'react';
import { storageToDoc } from '../utils/editorDoc';
import RichDocPreview from './RichDocPreview';

function formatDecimal(value, digits = 2) {
  if (value == null || Number.isNaN(Number(value))) return '-';
  return Number(value).toFixed(digits);
}

export default function AnalyticsPanel({
  attempts,
  allAttempts,
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
  const [questionFilters, setQuestionFilters] = useState({ questionNumber: '', itemId: '' });
  const [studentReportQuery, setStudentReportQuery] = useState('');
  const [previewRow, setPreviewRow] = useState(null);
  const [markedModalRow, setMarkedModalRow] = useState(null);

  const hasData = attempts.length > 0;
  const itemsById = useMemo(() => {
    const map = new Map();
    (items || []).forEach((item) => map.set(item.id, item));
    return map;
  }, [items]);

  const filteredQuestionRows = useMemo(() => {
    const questionQuery = questionFilters.questionNumber.trim();
    const itemQuery = questionFilters.itemId.trim();
    const questionNumbers = questionQuery
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean);
    const itemIds = itemQuery
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean);
    return questionStats.filter((row) => {
      if (questionNumbers.length > 0 && !questionNumbers.includes(String(row.questionNumber ?? ''))) {
        return false;
      }
      if (itemIds.length > 0 && !itemIds.includes(String(row.itemId ?? ''))) {
        return false;
      }
      return true;
    });
  }, [questionStats, questionFilters]);

  const sortedQuestionRows = useMemo(() => {
    const rows = [...filteredQuestionRows];
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
  }, [filteredQuestionRows, sortBy, sortDir]);

  const chartRows = useMemo(
    () => [...sortedQuestionRows].sort((a, b) => b.incorrect - a.incorrect).slice(0, 12),
    [sortedQuestionRows],
  );

  const rankingRows = useMemo(() => {
    return [...attempts]
      .sort((a, b) => {
        const as = Number(a.score_percent);
        const bs = Number(b.score_percent);
        const aValid = Number.isFinite(as);
        const bValid = Number.isFinite(bs);
        if (aValid && bValid && bs !== as) return bs - as;
        if (aValid && !bValid) return -1;
        if (!aValid && bValid) return 1;
        const ac = String(a.created_at || '');
        const bc = String(b.created_at || '');
        return bc.localeCompare(ac);
      })
      .map((row, index) => ({ ...row, rank: index + 1 }));
  }, [attempts]);

  const studentReportRows = useMemo(() => {
    const query = studentReportQuery.trim().toLowerCase();
    if (!query) return [];
    return [...allAttempts]
      .filter((row) => {
        const haystack = [
          row.student_name,
          row.student_document_number,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return haystack.includes(query);
      })
      .sort((a, b) => {
        const as = String(a.student_name || '');
        const bs = String(b.student_name || '');
        const byStudent = as.localeCompare(bs);
        if (byStudent !== 0) return byStudent;
        const ac = String(a.created_at || '');
        const bc = String(b.created_at || '');
        return bc.localeCompare(ac);
      });
  }, [allAttempts, studentReportQuery]);

  function exportRankingCsv() {
    const headers = [
      'Rank',
      'Estudiante',
      'Grupo',
      'Examen',
      'Version',
      'Puntaje',
      'Correctas',
      'Incorrectas',
      'No marcadas',
      'Estado',
    ];
    const escape = (value) => {
      const text = String(value ?? '');
      if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
      return text;
    };
    const rows = rankingRows.map((row) => [
      row.rank,
      row.student_name || '-',
      row.student_group || '-',
      row.exam_title || '-',
      row.exam_version_code || '-',
      row.score_percent ?? '-',
      row.correct_count ?? '-',
      row.incorrect_count ?? '-',
      row.blank_count ?? '-',
      row.status || '-',
    ]);
    const csv = `${[headers, ...rows].map((line) => line.map(escape).join(',')).join('\n')}\n`;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ranking_calificaciones.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

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
  const selectedExamCodes = Array.isArray(filters.examCode) ? filters.examCode : [];
  const selectedGroups = Array.isArray(filters.group) ? filters.group : [];

  function getMultiSelectValues(event) {
    return Array.from(event.target.selectedOptions, (option) => option.value);
  }

  return (
    <section className="card">
      <h3>Analiticas</h3>
      <div className="filters-grid">
        <label>
          Codigo examen
          <select
            multiple
            size={Math.min(Math.max(examCodeOptions.length, 2), 6)}
            value={selectedExamCodes}
            onChange={(event) => onFilterChange({ ...filters, examCode: getMultiSelectValues(event) })}
          >
            {examCodeOptions.map((code) => (
              <option key={code} value={code}>{code}</option>
            ))}
          </select>
          <small className="helper-text">Ctrl o Cmd + clic para seleccionar varios.</small>
        </label>
        <label>
          Grupo
          <select
            multiple
            size={Math.min(Math.max(groupOptions.length, 2), 6)}
            value={selectedGroups}
            onChange={(event) => onFilterChange({ ...filters, group: getMultiSelectValues(event) })}
          >
            {groupOptions.map((group) => (
              <option key={group} value={group}>{group}</option>
            ))}
          </select>
          <small className="helper-text">Ctrl o Cmd + clic para seleccionar varios.</small>
        </label>
        <label>
          <span>&nbsp;</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              type="button"
              onClick={() => onFilterChange({ ...filters, examCode: [], group: [] })}
              disabled={!selectedExamCodes.length && !selectedGroups.length}
            >
              Limpiar filtros
            </button>
            <button type="button" onClick={onRefresh} disabled={loading}>
              {loading ? 'Calculando...' : 'Recalcular'}
            </button>
          </div>
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

      <div className="row between center">
        <h4>Informe por estudiante</h4>
        <span className="helper-text">{studentReportRows.length} resultado{studentReportRows.length === 1 ? '' : 's'}</span>
      </div>
      <div className="filters-grid">
        <label>
          Buscar estudiante
          <input
            type="text"
            placeholder="Nombre o numero de documento"
            value={studentReportQuery}
            onChange={(event) => setStudentReportQuery(event.target.value)}
          />
        </label>
        <label>
          <span>&nbsp;</span>
          <button
            type="button"
            onClick={() => setStudentReportQuery('')}
            disabled={!studentReportQuery}
          >
            Limpiar busqueda
          </button>
        </label>
      </div>

      {!studentReportQuery ? (
        <p className="helper-text">Escribe un nombre o numero de documento para ver los examenes presentados por ese estudiante.</p>
      ) : null}

      {studentReportQuery && studentReportRows.length ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Documento</th>
                <th>Grupo</th>
                <th>Codigo OMR</th>
                <th>Examen</th>
                <th>Version</th>
                <th>Puntaje</th>
                <th>Correctas</th>
                <th>Incorrectas</th>
                <th>No marcadas</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {studentReportRows.map((row) => (
                <tr key={`student-report-${row.attempt_id}`}>
                  <td>{row.student_name || '-'}</td>
                  <td>{row.student_document_number || '-'}</td>
                  <td>{row.student_group || '-'}</td>
                  <td>{row.exam_code || '-'}</td>
                  <td>{row.exam_title || '-'}</td>
                  <td>{row.exam_version_code || '-'}</td>
                  <td>{row.score_percent ?? '-'}</td>
                  <td>{row.correct_count ?? '-'}</td>
                  <td>{row.incorrect_count ?? '-'}</td>
                  <td>{row.blank_count ?? '-'}</td>
                  <td>{row.status || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {studentReportQuery && !studentReportRows.length ? (
        <p>No se encontraron resultados para ese estudiante con los filtros actuales.</p>
      ) : null}

      {!hasData ? <p>No hay intentos para analizar con los filtros actuales.</p> : null}

      {hasData ? (
        <>
          <div className="row between center">
            <h4>Ranking de calificaciones</h4>
            <button type="button" onClick={exportRankingCsv} disabled={!rankingRows.length}>
              Exportar CSV
            </button>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Estudiante</th>
                  <th>Grupo</th>
                  <th>Examen</th>
                  <th>Version</th>
                  <th>Puntaje</th>
                  <th>Correctas</th>
                  <th>Incorrectas</th>
                  <th>No marcadas</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {rankingRows.map((row) => (
                  <tr key={row.attempt_id}>
                    <td>{row.rank}</td>
                    <td>{row.student_name || '-'}</td>
                    <td>{row.student_group || '-'}</td>
                    <td>{row.exam_title || '-'}</td>
                    <td>{row.exam_version_code || '-'}</td>
                    <td>{row.score_percent ?? '-'}</td>
                    <td>{row.correct_count ?? '-'}</td>
                    <td>{row.incorrect_count ?? '-'}</td>
                    <td>{row.blank_count ?? '-'}</td>
                    <td>{row.status || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

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

          <div className="row between center">
            <h4>Resultados por pregunta</h4>
            <button
              type="button"
              onClick={() => setQuestionFilters({ questionNumber: '', itemId: '' })}
              disabled={!questionFilters.questionNumber && !questionFilters.itemId}
            >
              Limpiar filtros
            </button>
          </div>
        <div className="filters-grid">
          <label>
            Numero de pregunta
            <input
              type="text"
              inputMode="numeric"
              placeholder="Ej: 12, 15, 18"
              value={questionFilters.questionNumber}
              onChange={(event) =>
                setQuestionFilters((prev) => ({ ...prev, questionNumber: event.target.value }))
              }
            />
          </label>
          <label>
            ID item
            <input
              type="text"
              inputMode="numeric"
              placeholder="Ej: 345, 410, 512"
              value={questionFilters.itemId}
              onChange={(event) =>
                setQuestionFilters((prev) => ({ ...prev, itemId: event.target.value }))
              }
            />
          </label>
        </div>
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
