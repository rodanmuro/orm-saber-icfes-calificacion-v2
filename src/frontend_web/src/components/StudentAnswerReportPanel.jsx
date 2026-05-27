import { useMemo, useState } from 'react';
import { storageToDoc } from '../utils/editorDoc';
import RichDocPreview from './RichDocPreview';

function formatDateTime(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function splitCsvValues(value) {
  return String(value || '')
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function exportStudentReportToExcel({ studentSummary, rows }) {
  const filenameBase = studentSummary?.student_document_number
    ? `informe_estudiante_${studentSummary.student_document_number}`
    : 'informe_estudiante';
  const tableRows = rows
    .map(
      (row) => `
        <tr>
          <td>${escapeHtml(formatDateTime(row.created_at))}</td>
          <td>${escapeHtml(row.exam_code || '-')}</td>
          <td>${escapeHtml(row.exam_title || '-')}</td>
          <td>${escapeHtml(row.exam_version_code || '-')}</td>
          <td>${escapeHtml(row.question_number ?? '-')}</td>
          <td>${escapeHtml(row.item_id ?? '-')}</td>
          <td>${escapeHtml(row.standard_name || '-')}</td>
          <td>${escapeHtml(row.competency_name || '-')}</td>
          <td>${escapeHtml(row.effective_answer || row.marked_answer || '-')}</td>
          <td>${escapeHtml(row.correct_answer || '-')}</td>
          <td>${escapeHtml(row.effective_status || '-')}</td>
        </tr>`,
    )
    .join('');

  const html = `
    <html>
      <head>
        <meta charset="utf-8" />
      </head>
      <body>
        <table border="1">
          <tr><th colspan="2">Informe estudiante</th></tr>
          <tr><td><strong>Estudiante</strong></td><td>${escapeHtml(studentSummary?.student_name || '-')}</td></tr>
          <tr><td><strong>Documento</strong></td><td style="mso-number-format:'\\@';">${escapeHtml(studentSummary?.student_document_number || '-')}</td></tr>
          <tr><td><strong>Grupo</strong></td><td>${escapeHtml(studentSummary?.student_group || '-')}</td></tr>
          <tr><td><strong>Total respuestas</strong></td><td>${escapeHtml(rows.length)}</td></tr>
        </table>
        <br />
        <table border="1">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Codigo OMR</th>
              <th>Examen</th>
              <th>Version</th>
              <th>Pregunta</th>
              <th>ID item</th>
              <th>Estandar</th>
              <th>Competencia</th>
              <th>Marcada</th>
              <th>Correcta</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            ${tableRows}
          </tbody>
        </table>
      </body>
    </html>
  `;

  const blob = new Blob([`\ufeff${html}`], {
    type: 'application/vnd.ms-excel;charset=utf-8;',
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${filenameBase}.xls`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

export default function StudentAnswerReportPanel({
  rows,
  items,
  students,
  loading,
  searchQuery,
  onSearchQueryChange,
  onSearch,
}) {
  const [tableFilters, setTableFilters] = useState({
    standard: '',
    competency: '',
    status: '',
    examCode: '',
    itemId: '',
    questionNumber: '',
  });
  const [sortBy, setSortBy] = useState('created_at');
  const [sortDir, setSortDir] = useState('desc');
  const [previewRow, setPreviewRow] = useState(null);

  const itemsById = useMemo(() => {
    const map = new Map();
    (items || []).forEach((item) => map.set(item.id, item));
    return map;
  }, [items]);

  const standardOptions = useMemo(() => {
    const values = new Set();
    rows.forEach((row) => {
      if (row.standard_name) values.add(String(row.standard_name));
    });
    return Array.from(values).sort();
  }, [rows]);

  const competencyOptions = useMemo(() => {
    const values = new Set();
    rows.forEach((row) => {
      if (row.competency_name) values.add(String(row.competency_name));
    });
    return Array.from(values).sort();
  }, [rows]);

  const statusOptions = useMemo(() => {
    const values = new Set();
    rows.forEach((row) => {
      if (row.effective_status) values.add(String(row.effective_status));
    });
    return Array.from(values).sort();
  }, [rows]);

  const filteredRows = useMemo(() => {
    const selectedExamCodes = splitCsvValues(tableFilters.examCode);
    const selectedItemIds = splitCsvValues(tableFilters.itemId);
    const selectedQuestionNumbers = splitCsvValues(tableFilters.questionNumber);
    return rows.filter((row) => {
      if (tableFilters.standard && String(row.standard_name || '') !== tableFilters.standard) return false;
      if (tableFilters.competency && String(row.competency_name || '') !== tableFilters.competency) return false;
      if (tableFilters.status && String(row.effective_status || '') !== tableFilters.status) return false;
      if (selectedExamCodes.length > 0 && !selectedExamCodes.includes(String(row.exam_code || ''))) return false;
      if (selectedItemIds.length > 0 && !selectedItemIds.includes(String(row.item_id || ''))) return false;
      if (selectedQuestionNumbers.length > 0 && !selectedQuestionNumbers.includes(String(row.question_number || ''))) {
        return false;
      }
      return true;
    });
  }, [rows, tableFilters]);

  const sortedRows = useMemo(() => {
    const next = [...filteredRows];
    next.sort((a, b) => {
      const av = a?.[sortBy];
      const bv = b?.[sortBy];
      if (sortBy === 'created_at') {
        const ad = new Date(av || 0).getTime();
        const bd = new Date(bv || 0).getTime();
        return sortDir === 'asc' ? ad - bd : bd - ad;
      }
      if (typeof av === 'number' && typeof bv === 'number') {
        return sortDir === 'asc' ? av - bv : bv - av;
      }
      const as = String(av ?? '');
      const bs = String(bv ?? '');
      return sortDir === 'asc' ? as.localeCompare(bs) : bs.localeCompare(as);
    });
    return next;
  }, [filteredRows, sortBy, sortDir]);

  function toggleSort(key) {
    if (sortBy === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
      return;
    }
    setSortBy(key);
    setSortDir(key === 'created_at' ? 'desc' : 'asc');
  }

  function sortMark(key) {
    if (sortBy !== key) return '';
    return sortDir === 'asc' ? ' ↑' : ' ↓';
  }

  function clearFilters() {
    setTableFilters({
      standard: '',
      competency: '',
      status: '',
      examCode: '',
      itemId: '',
      questionNumber: '',
    });
  }

  const previewItem = previewRow?.item_id ? itemsById.get(previewRow.item_id) : null;
  const studentSummary = sortedRows.length > 0
    ? {
        student_name: sortedRows[0].student_name,
        student_document_number: sortedRows[0].student_document_number,
        student_group: sortedRows[0].student_group,
      }
    : null;

  return (
    <section className="card">
      <div className="row between center">
        <h3>Informe estudiante</h3>
        <span className="helper-text">{sortedRows.length} respuesta{sortedRows.length === 1 ? '' : 's'}</span>
      </div>

      <div className="filters-grid">
        <label>
          Buscar estudiante
          <input
            type="text"
            list="students-answer-report-list"
            placeholder="Nombre o numero de documento"
            value={searchQuery}
            onChange={(event) => onSearchQueryChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') onSearch();
            }}
          />
          <datalist id="students-answer-report-list">
            {(students || []).map((student) => (
              <option
                key={student.id}
                value={`${student.document_number} - ${student.first_name} ${student.last_name}`}
              />
            ))}
          </datalist>
        </label>
        <label>
          <span>&nbsp;</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button type="button" onClick={onSearch} disabled={loading || !searchQuery.trim()}>
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
            <button
              type="button"
              onClick={() => {
                onSearchQueryChange('');
                clearFilters();
              }}
              disabled={!searchQuery && !rows.length}
            >
              Limpiar
            </button>
          </div>
        </label>
      </div>

      <div className="filters-grid">
        <label>
          Estandar
          <select
            value={tableFilters.standard}
            onChange={(event) => setTableFilters((prev) => ({ ...prev, standard: event.target.value }))}
          >
            <option value="">Todos</option>
            {standardOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label>
          Competencia
          <select
            value={tableFilters.competency}
            onChange={(event) => setTableFilters((prev) => ({ ...prev, competency: event.target.value }))}
          >
            <option value="">Todas</option>
            {competencyOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label>
          Estado
          <select
            value={tableFilters.status}
            onChange={(event) => setTableFilters((prev) => ({ ...prev, status: event.target.value }))}
          >
            <option value="">Todos</option>
            {statusOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label>
          Codigo OMR
          <input
            type="text"
            placeholder="Ej: 2, 5"
            value={tableFilters.examCode}
            onChange={(event) => setTableFilters((prev) => ({ ...prev, examCode: event.target.value }))}
          />
        </label>
        <label>
          Numero pregunta
          <input
            type="text"
            placeholder="Ej: 4, 18"
            value={tableFilters.questionNumber}
            onChange={(event) => setTableFilters((prev) => ({ ...prev, questionNumber: event.target.value }))}
          />
        </label>
        <label>
          ID item
          <input
            type="text"
            placeholder="Ej: 120, 121"
            value={tableFilters.itemId}
            onChange={(event) => setTableFilters((prev) => ({ ...prev, itemId: event.target.value }))}
          />
        </label>
      </div>

      <div className="row between center">
        <p className="helper-text">Usa filtros para detectar patrones por estandar, competencia o tipo de error.</p>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={() => exportStudentReportToExcel({ studentSummary, rows: sortedRows })}
            disabled={!sortedRows.length}
          >
            Exportar a Excel
          </button>
          <button
            type="button"
            onClick={clearFilters}
            disabled={Object.values(tableFilters).every((value) => !value)}
          >
            Limpiar filtros
          </button>
        </div>
      </div>

      {!searchQuery.trim() ? (
        <p className="helper-text">Busca un estudiante por nombre o documento para cargar el informe detallado.</p>
      ) : null}

      {searchQuery.trim() && !loading && !rows.length ? (
        <p>No se encontraron respuestas para ese estudiante.</p>
      ) : null}

      {studentSummary ? (
        <div className="analytics-summary-grid">
          <div className="analytics-card">
            <span className="analytics-label">Estudiante</span>
            <strong>{studentSummary.student_name || '-'}</strong>
          </div>
          <div className="analytics-card">
            <span className="analytics-label">Documento</span>
            <strong>{studentSummary.student_document_number || '-'}</strong>
          </div>
          <div className="analytics-card">
            <span className="analytics-label">Grupo</span>
            <strong>{studentSummary.student_group || '-'}</strong>
          </div>
        </div>
      ) : null}

      {sortedRows.length ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('created_at')}>
                    Fecha{sortMark('created_at')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('exam_code')}>
                    Codigo OMR{sortMark('exam_code')}
                  </button>
                </th>
                <th>Examen</th>
                <th>Version</th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('question_number')}>
                    Pregunta{sortMark('question_number')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('item_id')}>
                    ID item{sortMark('item_id')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('standard_name')}>
                    Estandar{sortMark('standard_name')}
                  </button>
                </th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('competency_name')}>
                    Competencia{sortMark('competency_name')}
                  </button>
                </th>
                <th>Marcada</th>
                <th>Correcta</th>
                <th>
                  <button type="button" className="sort-btn" onClick={() => toggleSort('effective_status')}>
                    Estado{sortMark('effective_status')}
                  </button>
                </th>
                <th>Ver</th>
              </tr>
            </thead>
            <tbody>
              {sortedRows.map((row) => (
                <tr key={`${row.attempt_id}-${row.question_number}-${row.item_id || 'na'}`}>
                  <td>{formatDateTime(row.created_at)}</td>
                  <td>{row.exam_code || '-'}</td>
                  <td>{row.exam_title || '-'}</td>
                  <td>{row.exam_version_code || '-'}</td>
                  <td>{row.question_number ?? '-'}</td>
                  <td>{row.item_id ?? '-'}</td>
                  <td>{row.standard_name || '-'}</td>
                  <td>{row.competency_name || '-'}</td>
                  <td>{row.effective_answer || row.marked_answer || '-'}</td>
                  <td>{row.correct_answer || '-'}</td>
                  <td>{row.effective_status || '-'}</td>
                  <td>
                    <button
                      type="button"
                      onClick={() => setPreviewRow(row)}
                      disabled={!row.item_id || !itemsById.get(row.item_id)}
                    >
                      Ver
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {previewRow ? (
        <div className="preview-modal-overlay" onClick={() => setPreviewRow(null)}>
          <div className="preview-modal" onClick={(event) => event.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>
                Pregunta {previewRow.question_number} | Item #{previewRow.item_id || '-'} | OMR {previewRow.exam_code || '-'}
              </h4>
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
              <p>No se encontro el item asociado.</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
