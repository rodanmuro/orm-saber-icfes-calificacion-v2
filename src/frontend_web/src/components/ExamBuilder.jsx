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
  onPublishVersion,
  onExportExamPdf,
  onExportExamDocx,
  exporting,
  loading,
}) {
  const [form, setForm] = useState(emptyExamForm(exams[0]?.teacher_id || 1));
  const [previewModalItem, setPreviewModalItem] = useState(null);
  const [previewModalContext, setPreviewModalContext] = useState(null);

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

  const itemsById = useMemo(() => {
    const map = new Map();
    items.forEach((item) => map.set(item.id, item));
    return map;
  }, [items]);

  const availableItemIds = useMemo(() => itemsNotAdded.map((item) => item.id), [itemsNotAdded]);
  const assignedItemIds = useMemo(
    () => (selectedExam ? selectedExam.items.map((row) => row.item_id) : []),
    [selectedExam],
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
                    <th>Exportar</th>
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
                      <td className="col-action col-export">
                        <div className="export-actions">
                          <button
                            type="button"
                            onClick={() => onExportExamPdf(exam)}
                            disabled={exporting?.examId === exam.id}
                          >
                            {exporting?.examId === exam.id && exporting?.format === 'pdf' ? 'Generando...' : 'PDF'}
                          </button>
                          <button
                            type="button"
                            onClick={() => onExportExamDocx(exam)}
                            disabled={exporting?.examId === exam.id}
                          >
                            {exporting?.examId === exam.id && exporting?.format === 'docx' ? 'Generando...' : 'DOCX'}
                          </button>
                        </div>
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
            Examen seleccionado: #{selectedExam.id} - {selectedExam.exam_code}
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
                    <th>Code</th>
                    <th>Seed</th>
                    <th>Preguntas barajadas</th>
                    <th>Opciones barajadas</th>
                  </tr>
                </thead>
                <tbody>
                  {versions.map((version) => (
                    <tr key={version.id}>
                      <td>{version.id}</td>
                      <td>{version.version_code}</td>
                      <td>{version.seed_shuffle}</td>
                      <td>{version.shuffle_questions ? 'Si' : 'No'}</td>
                      <td>{version.shuffle_options ? 'Si' : 'No'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}

          <div className="grid grid-2">
            <div className="exam-items-pane">
              <h5>Items disponibles ({itemsNotAdded.length})</h5>
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
                    {itemsNotAdded.map((item) => (
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
              <h5>Items asociados (orden inicial) ({selectedExam.items.length})</h5>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Orden</th>
                      <th>Item ID</th>
                      <th>Enunciado</th>
                      <th>Estandar</th>
                      <th>Desempeño</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedExam.items.map((row) => (
                      <tr key={`${row.exam_id}-${row.item_id}`}>
                        <td>{row.order_position}</td>
                        <td>{row.item_id}</td>
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
    </section>
  );
}
