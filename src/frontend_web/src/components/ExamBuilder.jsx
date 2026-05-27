import { useEffect, useMemo, useState } from 'react';
import { docHasMeaningfulContent, docToPlainText, storageToDoc } from '../utils/editorDoc';
import RichDocPreview from './RichDocPreview';

function emptyExamForm(defaultTeacherId) {
  return {
    teacher_id: defaultTeacherId || 1,
    title: '',
    description: '',
  };
}

function statementPreview(value) {
  const doc = storageToDoc(value);
  const text = docToPlainText(doc);
  if (!text && docHasMeaningfulContent(doc)) return '[contenido no textual]';
  if (!text) return '-';
  return text;
}

function splitCsvValues(value) {
  return String(value || '')
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function getGroupVisual(groupKey) {
  const normalized = String(groupKey || '').trim();
  if (!normalized) {
    return {
      label: 'Sin bloque',
      rowStyle: undefined,
      badgeStyle: undefined,
    };
  }

  const numeric = Number(normalized);
  const hue = Number.isFinite(numeric) ? (numeric * 47) % 360 : 210;
  const accent = `hsl(${hue} 65% 42%)`;
  const soft = `hsl(${hue} 75% 94%)`;
  const border = `hsl(${hue} 55% 78%)`;

  return {
    label: `Bloque ${normalized}`,
    rowStyle: {
      background: soft,
      boxShadow: `inset 4px 0 0 ${accent}`,
    },
    badgeStyle: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      minWidth: '44px',
      padding: '3px 8px',
      borderRadius: '999px',
      border: `1px solid ${border}`,
      background: soft,
      color: accent,
      fontWeight: 700,
      fontSize: '12px',
    },
  };
}

export default function ExamBuilder({
  items,
  exams,
  selectedExam,
  versions,
  onRefreshExams,
  onCreateExam,
  onSelectExam,
  onAddItem,
  onRemoveItem,
  onUpdateExamItem,
  onPublishVersion,
  onDeleteVersion,
  onExportExamPdf,
  onExportExamDocx,
  onViewVersionAnswerKey,
  onGetVersionDetail,
  onReorderVersion,
  answerKeyModal,
  onCloseAnswerKeyModal,
  exporting,
  loadingAnswerKey,
  loading,
}) {
  const [form, setForm] = useState(emptyExamForm(exams[0]?.teacher_id || 1));
  const [previewModalItem, setPreviewModalItem] = useState(null);
  const [previewModalContext, setPreviewModalContext] = useState(null);
  const [availableStandardFilter, setAvailableStandardFilter] = useState('');
  const [availableItemIdFilter, setAvailableItemIdFilter] = useState('');
  const [assignedStandardFilter, setAssignedStandardFilter] = useState('');
  const [assignedItemIdFilter, setAssignedItemIdFilter] = useState('');
  const [assignedGroupFilter, setAssignedGroupFilter] = useState('');
  const [groupDrafts, setGroupDrafts] = useState({});
  const [savingGroupItemId, setSavingGroupItemId] = useState(null);
  const [reorderModal, setReorderModal] = useState({
    open: false,
    exam: null,
    version: null,
    rows: [],
    loading: false,
    saving: false,
    dragId: null,
  });

  useEffect(() => {
    if (!Number.isFinite(form.teacher_id) || form.teacher_id <= 0) return;
    onRefreshExams(form.teacher_id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.teacher_id]);

  const itemsNotAdded = useMemo(() => {
    if (!selectedExam) return [];
    const existing = new Set(selectedExam.items.map((row) => row.item_id));
    return items.filter(
      (item) =>
        item.teacher_id === selectedExam.teacher_id &&
        !existing.has(item.id)
    );
  }, [items, selectedExam]);

  const availableStandardOptions = useMemo(() => {
    const values = new Set();
    itemsNotAdded.forEach((item) => {
      const standardName = item.curriculum?.standard_name;
      if (standardName) values.add(String(standardName));
    });
    return Array.from(values).sort();
  }, [itemsNotAdded]);

  const itemsById = useMemo(() => {
    const map = new Map();
    items.forEach((item) => map.set(item.id, item));
    return map;
  }, [items]);

  const filteredAvailableItems = useMemo(() => {
    const query = availableStandardFilter.trim().toLowerCase();
    const selectedItemIds = new Set(splitCsvValues(availableItemIdFilter));
    return itemsNotAdded.filter((item) => {
      if (query && !String(item.curriculum?.standard_name || '').toLowerCase().includes(query)) {
        return false;
      }
      if (selectedItemIds.size > 0 && !selectedItemIds.has(String(item.id))) {
        return false;
      }
      return true;
    });
  }, [availableItemIdFilter, availableStandardFilter, itemsNotAdded]);

  const assignedStandardOptions = useMemo(() => {
    if (!selectedExam) return [];
    const values = new Set();
    selectedExam.items.forEach((row) => {
      const standardName = itemsById.get(row.item_id)?.curriculum?.standard_name;
      if (standardName) values.add(String(standardName));
    });
    return Array.from(values).sort();
  }, [itemsById, selectedExam]);

  const assignedRowsByItemId = useMemo(() => {
    const map = new Map();
    (selectedExam?.items || []).forEach((row) => {
      map.set(row.item_id, row);
    });
    return map;
  }, [selectedExam]);

  const assignedGroupOptions = useMemo(() => {
    if (!selectedExam) return [];
    const values = new Set();
    selectedExam.items.forEach((row) => {
      const groupKey = String(row.group_key || '').trim();
      if (groupKey) values.add(groupKey);
    });
    return Array.from(values).sort();
  }, [selectedExam]);

  const filteredAssignedItems = useMemo(() => {
    if (!selectedExam) return [];
    const query = assignedStandardFilter.trim().toLowerCase();
    const selectedItemIds = new Set(splitCsvValues(assignedItemIdFilter));
    const selectedGroups = new Set(splitCsvValues(assignedGroupFilter).map((value) => String(value)));
    return selectedExam.items.filter((row) => {
      if (query && !String(itemsById.get(row.item_id)?.curriculum?.standard_name || '').toLowerCase().includes(query)) {
        return false;
      }
      if (selectedItemIds.size > 0 && !selectedItemIds.has(String(row.item_id))) {
        return false;
      }
      if (selectedGroups.size > 0 && !selectedGroups.has(String(row.group_key || ''))) {
        return false;
      }
      return true;
    });
  }, [assignedGroupFilter, assignedItemIdFilter, assignedStandardFilter, itemsById, selectedExam]);

  const availableItemIds = useMemo(() => filteredAvailableItems.map((item) => item.id), [filteredAvailableItems]);
  const assignedItemIds = useMemo(
    () => filteredAssignedItems.map((row) => row.item_id),
    [filteredAssignedItems],
  );

  const buildCellText = (value, maxLen = 70) => {
    const full = (value || '-').toString();
    if (full.length <= maxLen) return { short: full, full };
    return { short: `${full.slice(0, maxLen)}...`, full };
  };

  useEffect(() => {
    if (!selectedExam) {
      setPreviewModalItem(null);
      setPreviewModalContext(null);
    }
  }, [selectedExam]);

  useEffect(() => {
    if (!selectedExam) {
      setGroupDrafts({});
      return;
    }
    const nextDrafts = {};
    selectedExam.items.forEach((row) => {
      nextDrafts[row.item_id] = row.group_key || '';
    });
    setGroupDrafts(nextDrafts);
  }, [selectedExam]);

  useEffect(() => {
    if (!selectedExam) {
      setAvailableStandardFilter('');
      setAvailableItemIdFilter('');
      setAssignedStandardFilter('');
      setAssignedItemIdFilter('');
      setAssignedGroupFilter('');
    }
  }, [selectedExam]);

  async function saveGroupKey(itemId) {
    if (!selectedExam || !onUpdateExamItem) return;
    setSavingGroupItemId(itemId);
    try {
      await onUpdateExamItem(selectedExam.id, itemId, { group_key: groupDrafts[itemId] || null });
    } finally {
      setSavingGroupItemId(null);
    }
  }

  function openPreviewByItem(item, context) {
    if (!item) return;
    setPreviewModalItem(item);
    setPreviewModalContext(context || null);
  }

  function openPreviewByExamRow(row, context) {
    const fromList = itemsById.get(row.item_id);
    if (fromList) {
      setPreviewModalItem(fromList);
      setPreviewModalContext(context || null);
      return;
    }
    setPreviewModalItem({
      id: row.item_id,
      statement: row.item_statement,
      options: {},
      correct_answer: null,
    });
    setPreviewModalContext(context || null);
  }

  function getContextIds() {
    if (previewModalContext === 'available') return availableItemIds;
    if (previewModalContext === 'assigned') return assignedItemIds;
    return [];
  }

  function navigatePreview(step) {
    if (!previewModalItem) return;
    const ids = getContextIds();
    if (!ids.length) return;
    const idx = ids.findIndex((id) => id === previewModalItem.id);
    if (idx < 0) return;
    const nextIdx = idx + step;
    if (nextIdx < 0 || nextIdx >= ids.length) return;
    const nextItem = itemsById.get(ids[nextIdx]);
    if (!nextItem) return;
    setPreviewModalItem(nextItem);
  }

  function exportAnswerKeyCsv() {
    if (!answerKeyModal?.rows?.length) return;
    const escapeCsv = (value) => {
      const text = String(value ?? '');
      if (/[",\n]/.test(text)) {
        return `"${text.replace(/"/g, '""')}"`;
      }
      return text;
    };

    const header = ['Pregunta', 'Respuesta Correcta', 'Item ID'];
    const lines = [
      header.join(','),
      ...answerKeyModal.rows.map((row) => [
        row.question_number,
        row.correct_answer,
        row.item_id,
      ].map(escapeCsv).join(',')),
    ];
    const csv = `${lines.join('\n')}\n`;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    const examCode = answerKeyModal.version?.exam_code || answerKeyModal.exam?.exam_code || answerKeyModal.exam?.id || 'exam';
    const versionCode = answerKeyModal.version?.version_code || 'base';
    a.href = url;
    a.download = `clave_respuestas_exam_${examCode}_v${versionCode}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }

  async function openReorderModal(version) {
    if (!selectedExam || !onGetVersionDetail) return;
    setReorderModal((prev) => ({ ...prev, open: true, exam: selectedExam, version, rows: [], loading: true, saving: false, dragId: null }));
    try {
      const detail = await onGetVersionDetail(selectedExam.id, version.id);
      const statementByItemId = new Map((selectedExam.items || []).map((row) => [row.item_id, row.item_statement]));
      const rows = (detail.items || []).map((row) => ({
        versionItemId: row.id,
        itemId: row.item_id,
        questionNumber: row.question_number,
        statement: statementByItemId.get(row.item_id) || '',
      }));
      setReorderModal((prev) => ({ ...prev, rows, loading: false }));
    } catch (err) {
      setReorderModal((prev) => ({ ...prev, open: false, loading: false }));
      throw err;
    }
  }

  function closeReorderModal() {
    setReorderModal({ open: false, exam: null, version: null, rows: [], loading: false, saving: false, dragId: null });
  }

  function onDragStartRow(id) {
    setReorderModal((prev) => ({ ...prev, dragId: id }));
  }

  function onDropRow(targetId) {
    setReorderModal((prev) => {
      if (!prev.dragId || prev.dragId === targetId) return prev;
      const rows = [...prev.rows];
      const from = rows.findIndex((r) => r.versionItemId === prev.dragId);
      const to = rows.findIndex((r) => r.versionItemId === targetId);
      if (from < 0 || to < 0) return { ...prev, dragId: null };
      const [moved] = rows.splice(from, 1);
      rows.splice(to, 0, moved);
      return { ...prev, rows, dragId: null };
    });
  }

  async function saveReorderModal() {
    if (!reorderModal.exam || !reorderModal.version || !onReorderVersion) return;
    setReorderModal((prev) => ({ ...prev, saving: true }));
    try {
      await onReorderVersion(
        reorderModal.exam,
        reorderModal.version,
        reorderModal.rows.map((r) => r.versionItemId),
      );
      closeReorderModal();
    } finally {
      setReorderModal((prev) => ({ ...prev, saving: false }));
    }
  }

  return (
    <section className="card">
      <h3>Armado de examen</h3>

      <div className="grid grid-2">
        <label>
          Teacher ID
          <input
            type="number"
            min="1"
            value={form.teacher_id}
            onChange={(e) => setForm({ ...form, teacher_id: Number(e.target.value) })}
          />
        </label>
        <label>
          Titulo
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        </label>
        <label>
          Descripcion
          <input
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </label>
      </div>
      <p className="helper-text">Codigo de examen: se genera automaticamente por docente (1, 2, 3, ...).</p>

      <div className="actions">
        <button
          type="button"
          onClick={async () => {
            await onCreateExam(form);
            await onRefreshExams(form.teacher_id);
            setForm(emptyExamForm(form.teacher_id));
          }}
        >
          Crear examen
        </button>
      </div>

      <hr />

      <h4>Examenes del docente</h4>
      {loading ? <p>Cargando examenes...</p> : null}
      <div className="table-wrap">
        <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Code</th>
                    <th>Titulo</th>
                    <th>Accion</th>
                  </tr>
                </thead>
                <tbody>
                  {exams.map((exam) => (
                    <tr key={exam.id} className={selectedExam?.id === exam.id ? 'row-selected' : ''}>
                <td>{exam.id}</td>
                <td>{exam.exam_code}</td>
                <td>{exam.title}</td>
                      <td className="col-action">
                  <button type="button" onClick={() => onSelectExam(exam.id)}>
                    Abrir
                  </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

      {selectedExam ? (
        <>
          <hr />
          <h4>
            Examen seleccionado: #{selectedExam.id} - Código base {selectedExam.exam_code}
          </h4>
          <p className="helper-text">
            Docente del examen: {selectedExam.teacher_id}. Solo se listan items de este docente para asociar.
          </p>
          <div className="actions">
            <button
              type="button"
              onClick={() => onPublishVersion(selectedExam.id)}
              disabled={selectedExam.items.length === 0}
            >
              Publicar version (barajada)
            </button>
          </div>

          <h5>Versiones publicadas</h5>
          {versions.length === 0 ? <p>No hay versiones publicadas.</p> : null}
          {versions.length > 0 ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Código OMR</th>
                    <th>Versión</th>
                    <th>Seed</th>
                    <th>Preguntas barajadas</th>
                    <th>Opciones barajadas</th>
                    <th>Accion</th>
                    <th>Exportar</th>
                  </tr>
                </thead>
                <tbody>
                  {versions.map((version) => (
                    <tr key={version.id}>
                      <td>{version.id}</td>
                      <td>{version.exam_code}</td>
                      <td>{version.version_code}</td>
                      <td>{version.seed_shuffle}</td>
                      <td>{version.shuffle_questions ? 'Si' : 'No'}</td>
                      <td>{version.shuffle_options ? 'Si' : 'No'}</td>
                      <td className="col-action">
                        <button
                          type="button"
                          onClick={() => onViewVersionAnswerKey(selectedExam, version)}
                          disabled={loadingAnswerKey}
                        >
                          {loadingAnswerKey ? 'Consultando...' : 'Ver respuestas correctas'}
                        </button>
                        <button
                          type="button"
                          onClick={() => openReorderModal(version)}
                          disabled={reorderModal.loading || reorderModal.saving}
                        >
                          Reordenar preguntas
                        </button>
                        <button
                          type="button"
                          className="btn-danger"
                          onClick={() => onDeleteVersion(selectedExam, version)}
                        >
                          Borrar
                        </button>
                      </td>
                      <td className="col-action col-export">
                        <div className="export-actions">
                          <button
                            type="button"
                            onClick={() => onExportExamPdf(selectedExam, version)}
                            disabled={exporting?.examId === selectedExam?.id}
                          >
                            {exporting?.examId === selectedExam?.id && exporting?.format === 'pdf' ? 'Generando...' : 'PDF'}
                          </button>
                          <button
                            type="button"
                            onClick={() => onExportExamDocx(selectedExam, version)}
                            disabled={exporting?.examId === selectedExam?.id}
                          >
                            {exporting?.examId === selectedExam?.id && exporting?.format === 'docx' ? 'Generando...' : 'DOCX'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}

          <div className="grid grid-2">
            <div className="exam-items-pane">
              <div className="row between center">
                <h5>Items disponibles ({filteredAvailableItems.length})</h5>
                <div style={{ display: 'grid', gap: '8px', minWidth: '280px' }}>
                  <label>
                    <span>Filtrar por estandar</span>
                    <input
                      type="text"
                      list="available-standards-list"
                      value={availableStandardFilter}
                      onChange={(event) => setAvailableStandardFilter(event.target.value)}
                      placeholder="Escribe un estandar"
                    />
                    <datalist id="available-standards-list">
                      {availableStandardOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </datalist>
                  </label>
                  <label>
                    <span>Filtrar por ID item</span>
                    <input
                      type="text"
                      value={availableItemIdFilter}
                      onChange={(event) => setAvailableItemIdFilter(event.target.value)}
                      placeholder="Ej: 120,121,112"
                    />
                  </label>
                </div>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Enunciado</th>
                      <th>Estandar</th>
                      <th>Desempeño</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAvailableItems.map((item) => (
                      <tr key={item.id}>
                        <td>{item.id}</td>
                        <td>
                          {(() => {
                            const cell = buildCellText(statementPreview(item.statement), 90);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td>
                          {(() => {
                            const cell = buildCellText(item.curriculum?.standard_name || '-', 42);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td>
                          {(() => {
                            const cell = buildCellText(item.curriculum?.competency_name || '-', 42);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td className="col-action">
                          <button
                            type="button"
                            onClick={() => openPreviewByItem(item, 'available')}
                          >
                            Vista previa
                          </button>
                          <button type="button" onClick={() => onAddItem(selectedExam.id, item.id)}>
                            Asociar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="exam-items-pane">
              <div className="row between center">
                <h5>Items asociados (orden inicial) ({filteredAssignedItems.length})</h5>
                <div style={{ display: 'grid', gap: '8px', minWidth: '280px' }}>
                  <label>
                    <span>Filtrar por estandar</span>
                    <input
                      type="text"
                      list="assigned-standards-list"
                      value={assignedStandardFilter}
                      onChange={(event) => setAssignedStandardFilter(event.target.value)}
                      placeholder="Escribe un estandar"
                    />
                    <datalist id="assigned-standards-list">
                      {assignedStandardOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </datalist>
                  </label>
                  <label>
                    <span>Filtrar por ID item</span>
                    <input
                      type="text"
                      value={assignedItemIdFilter}
                      onChange={(event) => setAssignedItemIdFilter(event.target.value)}
                      placeholder="Ej: 120,121,112"
                    />
                  </label>
                  <label>
                    <span>Filtrar por bloque</span>
                    <input
                      type="text"
                      list="assigned-group-keys-list"
                      value={assignedGroupFilter}
                      onChange={(event) => setAssignedGroupFilter(event.target.value)}
                      placeholder="Ej: 1,2,3"
                    />
                  </label>
                </div>
              </div>
              <p className="helper-text">
                Si varios items comparten el mismo bloque, quedaran consecutivos al publicar una version barajada.
                El bloque puede moverse de posicion, pero sus preguntas se mantienen seguidas.
              </p>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Orden</th>
                      <th>Item ID</th>
                      <th>Bloque</th>
                      <th>Enunciado</th>
                      <th>Estandar</th>
                      <th>Desempeño</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAssignedItems.map((row) => (
                      <tr
                        key={`${row.exam_id}-${row.item_id}`}
                        style={row.group_key ? getGroupVisual(row.group_key).rowStyle : undefined}
                      >
                        <td>{row.order_position}</td>
                        <td>{row.item_id}</td>
                        <td>
                          <div style={{ display: 'flex', gap: '6px', minWidth: '180px' }}>
                            <input
                              type="text"
                              inputMode="numeric"
                              pattern="[0-9]*"
                              list="assigned-group-keys-list"
                              value={groupDrafts[row.item_id] ?? ''}
                              onChange={(event) =>
                                setGroupDrafts((prev) => ({ ...prev, [row.item_id]: event.target.value }))
                              }
                              onKeyDown={(event) => {
                                if (event.key === 'Enter') {
                                  event.preventDefault();
                                  saveGroupKey(row.item_id);
                                }
                              }}
                              placeholder="Ej: 1"
                            />
                            <datalist id="assigned-group-keys-list">
                              {assignedGroupOptions.map((option) => (
                                <option key={option} value={option}>{option}</option>
                              ))}
                            </datalist>
                            <button
                              type="button"
                              onClick={() => saveGroupKey(row.item_id)}
                              disabled={
                                savingGroupItemId === row.item_id ||
                                String(groupDrafts[row.item_id] ?? '').trim() === String(row.group_key || '').trim()
                              }
                            >
                              {savingGroupItemId === row.item_id ? '...' : 'Guardar'}
                            </button>
                          </div>
                          <small className="helper-text">
                            {row.group_key ? (
                              <span style={getGroupVisual(row.group_key).badgeStyle}>
                                {getGroupVisual(row.group_key).label}
                              </span>
                            ) : 'Sin bloque numerico'}
                          </small>
                        </td>
                        <td>
                          {(() => {
                            const cell = buildCellText(statementPreview(row.item_statement), 90);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td>
                          {(() => {
                            const item = itemsById.get(row.item_id);
                            const cell = buildCellText(item?.curriculum?.standard_name || '-', 42);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td>
                          {(() => {
                            const item = itemsById.get(row.item_id);
                            const cell = buildCellText(item?.curriculum?.competency_name || '-', 42);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td className="col-action">
                          <button
                            type="button"
                            onClick={() => openPreviewByExamRow(row, 'assigned')}
                          >
                            Vista previa
                          </button>
                          <button type="button" onClick={() => onRemoveItem(selectedExam.id, row.item_id)}>
                            Quitar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      ) : null}

      {previewModalItem ? (
        <div
          className="preview-modal-overlay"
          onClick={() => {
            setPreviewModalItem(null);
            setPreviewModalContext(null);
          }}
        >
          <div className="preview-modal" onClick={(event) => event.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>
                Vista previa item #{previewModalItem.id}{' '}
                {previewModalContext === 'available' ? '(por asignar)' : ''}
                {previewModalContext === 'assigned' ? '(asignado)' : ''}
              </h4>
              <div className="preview-modal-actions">
                <button
                  type="button"
                  onClick={() => navigatePreview(-1)}
                  disabled={
                    !previewModalItem ||
                    !getContextIds().length ||
                    getContextIds().findIndex((id) => id === previewModalItem.id) <= 0
                  }
                >
                  ← Anterior
                </button>
                <button
                  type="button"
                  onClick={() => navigatePreview(1)}
                  disabled={
                    !previewModalItem ||
                    !getContextIds().length ||
                    getContextIds().findIndex((id) => id === previewModalItem.id) >=
                      getContextIds().length - 1
                  }
                >
                  Siguiente →
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setPreviewModalItem(null);
                    setPreviewModalContext(null);
                  }}
                >
                  Cerrar
                </button>
              </div>
            </div>

            <div className="preview-modal-section">
              <h5>Enunciado</h5>
              <RichDocPreview value={storageToDoc(previewModalItem.statement)} />
            </div>

            <div className="preview-modal-options">
              <div className="preview-modal-section">
                <h5>Opcion A</h5>
                <RichDocPreview value={storageToDoc(previewModalItem.options?.A)} />
              </div>
              <div className="preview-modal-section">
                <h5>Opcion B</h5>
                <RichDocPreview value={storageToDoc(previewModalItem.options?.B)} />
              </div>
              <div className="preview-modal-section">
                <h5>Opcion C</h5>
                <RichDocPreview value={storageToDoc(previewModalItem.options?.C)} />
              </div>
              <div className="preview-modal-section">
                <h5>Opcion D</h5>
                <RichDocPreview value={storageToDoc(previewModalItem.options?.D)} />
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {reorderModal.open ? (
        <div className="preview-modal-overlay" onClick={closeReorderModal}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Reordenar versión (drag & drop)</h4>
              <button type="button" onClick={closeReorderModal}>Cerrar</button>
            </div>
            <p className="helper-text">
              Examen #{reorderModal.exam?.id} | Código OMR {reorderModal.version?.exam_code} | Versión {reorderModal.version?.version_code}
            </p>
            <p className="helper-text">
              Arrastra cada fila para cambiar el orden. Al guardar se actualizan número de pregunta y clave OMR.
            </p>
            {reorderModal.loading ? <p>Cargando preguntas...</p> : null}
            {!reorderModal.loading ? (
              <div className="table-wrap" style={{ maxHeight: 420 }}>
                <table>
                  <thead>
                    <tr>
                      <th>Nuevo #</th>
                      <th>Item</th>
                      <th>Bloque</th>
                      <th>Enunciado</th>
                      <th>Estandar</th>
                      <th>Desempeño</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reorderModal.rows.map((row, idx) => {
                      const assignedRow = assignedRowsByItemId.get(row.itemId);
                      const groupKey = assignedRow?.group_key || null;
                      const visual = getGroupVisual(groupKey);
                      return (
                      <tr
                        key={row.versionItemId}
                        draggable
                        onDragStart={() => onDragStartRow(row.versionItemId)}
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={() => onDropRow(row.versionItemId)}
                        style={{ cursor: 'grab', ...(visual.rowStyle || {}) }}
                      >
                        <td>{idx + 1}</td>
                        <td>{row.itemId}</td>
                        <td>
                          {groupKey ? <span style={visual.badgeStyle}>{visual.label}</span> : '-'}
                        </td>
                        <td>
                          {(() => {
                            const item = itemsById.get(row.itemId);
                            const full = item
                              ? statementPreview(item.statement)
                              : statementPreview(row.statement || '');
                            const cell = buildCellText(full, 90);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td>
                          {(() => {
                            const item = itemsById.get(row.itemId);
                            const cell = buildCellText(item?.curriculum?.standard_name || '-', 42);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                        <td>
                          {(() => {
                            const item = itemsById.get(row.itemId);
                            const cell = buildCellText(item?.curriculum?.competency_name || '-', 42);
                            return (
                              <span className="cell-truncate" title={cell.full}>
                                {cell.short}
                              </span>
                            );
                          })()}
                        </td>
                      </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : null}
            <div className="actions">
              <button type="button" onClick={saveReorderModal} disabled={reorderModal.loading || reorderModal.saving}>
                {reorderModal.saving ? 'Guardando...' : 'Guardar orden'}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {answerKeyModal?.open ? (
        <div className="preview-modal-overlay" onClick={onCloseAnswerKeyModal}>
          <div className="preview-modal answer-key-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>
                Clave de respuestas - Examen #{answerKeyModal.exam?.id} ({answerKeyModal.exam?.exam_code})
              </h4>
              <div className="preview-modal-actions">
                <button type="button" onClick={exportAnswerKeyCsv}>Exportar a CSV</button>
                <button type="button" onClick={onCloseAnswerKeyModal}>Cerrar</button>
              </div>
            </div>
            <p className="helper-text">
              Version: {answerKeyModal.version?.version_code} | Seed: {answerKeyModal.version?.seed_shuffle}
            </p>
            <div className="table-wrap">
              <table className="answer-key-table">
                <thead>
                  <tr>
                    <th>Pregunta</th>
                    <th>Respuesta correcta</th>
                    <th>Item ID</th>
                    <th>Bloque</th>
                  </tr>
                </thead>
                <tbody>
                  {answerKeyModal.rows.map((row) => {
                    const assignedRow = assignedRowsByItemId.get(row.item_id);
                    const groupKey = assignedRow?.group_key || null;
                    const visual = getGroupVisual(groupKey);
                    return (
                    <tr
                      key={`${row.question_number}-${row.item_id}`}
                      style={groupKey ? visual.rowStyle : undefined}
                    >
                      <td>{row.question_number}</td>
                      <td>{row.correct_answer}</td>
                      <td>{row.item_id}</td>
                      <td>
                        {groupKey ? <span style={visual.badgeStyle}>{visual.label}</span> : '-'}
                      </td>
                    </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
