import { useEffect, useMemo, useRef, useState } from 'react';

import { createItem, deleteItem, getItem, listItems, updateItem, API_BASE_URL } from './api/itemsApi';
import { listStudents } from './api/studentsApi';
import { getOmrAttempt, listOmrAttempts, updateOmrAttemptAnswers } from './api/omrApi';
import {
  addItemToExam,
  createExam,
  getExam,
  getExamVersion,
  listExams,
  listExamVersions,
  exportExamVersionPdf,
  exportExamVersionDocx,
  publishExamVersion,
  removeItemFromExam,
} from './api/examsApi';
import ExamBuilder from './components/ExamBuilder';
import FiltersBar from './components/FiltersBar';
import ItemForm, { emptyForm, formToPayload, itemToForm } from './components/ItemForm';
import ItemList from './components/ItemList';
import StudentList from './components/StudentList';
import AttemptList from './components/AttemptList';
import { docHasMeaningfulContent } from './utils/editorDoc';


function parseDeleteErrorDetail(errorMessage) {
  const raw = String(errorMessage || '');
  const marker = 'HTTP ';
  if (!raw.includes(marker)) return raw || 'Error desconocido';

  const idx = raw.indexOf(':');
  if (idx === -1) return raw;
  const body = raw.slice(idx + 1).trim();

  try {
    const parsed = JSON.parse(body);
    if (parsed && typeof parsed === 'object' && parsed.detail) {
      return String(parsed.detail);
    }
  } catch {
    // no-op
  }
  return body || raw;
}

function filterItems(items, filters) {
  const subject = filters.subject.trim().toLowerCase();
  const difficulty = filters.difficulty.trim().toLowerCase();
  const curricularTag = filters.curricularTag.trim().toLowerCase();

  return items.filter((item) => {
    if (subject && !(item.subject || '').toLowerCase().includes(subject)) return false;
    if (difficulty && !(item.difficulty || '').toLowerCase().includes(difficulty)) return false;

    if (curricularTag) {
      const label = `${item.curriculum?.standard_name || ''} ${item.curriculum?.competency_name || ''}`.toLowerCase();
      if (!label.includes(curricularTag)) return false;
    }

    return true;
  });
}

export default function App() {
  const [activeTab, setActiveTab] = useState('edit');
  const [items, setItems] = useState([]);
  const [selectedItemId, setSelectedItemId] = useState(null);
  const [form, setForm] = useState(emptyForm());
  const [filters, setFilters] = useState({ subject: '', difficulty: '', curricularTag: '' });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selectedItemIds, setSelectedItemIds] = useState([]);
  const [loadingExams, setLoadingExams] = useState(false);
  const [exams, setExams] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);
  const [examVersions, setExamVersions] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState({ examId: null, format: null });
  const [loadingAnswerKey, setLoadingAnswerKey] = useState(false);
  const [answerKeyModal, setAnswerKeyModal] = useState({
    open: false,
    exam: null,
    version: null,
    rows: [],
  });
  const [students, setStudents] = useState([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [studentFilters, setStudentFilters] = useState({ query: '', group: '' });
  const [studentSortKey, setStudentSortKey] = useState('id_asc');
  const [attempts, setAttempts] = useState([]);
  const [loadingAttempts, setLoadingAttempts] = useState(false);
  const [attemptModal, setAttemptModal] = useState({ open: false, detail: null });
  const [attemptImage, setAttemptImage] = useState(null);
  const [attemptEdits, setAttemptEdits] = useState({});
  const [savingAttempt, setSavingAttempt] = useState(false);
  const [pendingAttemptSave, setPendingAttemptSave] = useState(false);
  const attemptEditsRef = useRef({});
  const [attemptFilters, setAttemptFilters] = useState({ query: '', status: '', group: '' });

  async function refreshItems() {
    setLoading(true);
    setError('');
    try {
      const data = await listItems();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshStudents() {
    setLoadingStudents(true);
    setError('');
    try {
      const data = await listStudents();
      setStudents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingStudents(false);
    }
  }

  useEffect(() => {
    refreshItems();
  }, []);

  useEffect(() => {
    if (activeTab === 'students') {
      refreshStudents();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'graded') {
      refreshAttempts();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  useEffect(() => {
    if (activeTab !== 'graded') return;
    const timer = setInterval(() => {
      refreshAttempts();
    }, 5000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  async function refreshAttempts() {
    setLoadingAttempts(true);
    setError('');
    try {
      const data = await listOmrAttempts({ teacherId: 1 });
      setAttempts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAttempts(false);
    }
  }

  function buildManualValue(row) {
    if (row.manual_override) {
      return row.manual_answer ? row.manual_answer : '__blank__';
    }
    return '';
  }

  async function handleViewAttempt(row) {
    setError('');
    try {
      const detail = await getOmrAttempt(row.attempt_id);
      setAttemptModal({ open: true, detail });
      const nextEdits = {};
      detail.answers.forEach((answer) => {
        nextEdits[answer.question_number] = buildManualValue(answer);
      });
      setAttemptEdits(nextEdits);
      attemptEditsRef.current = nextEdits;
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAttemptEditChange(questionNumber, value) {
    const nextEdits = { ...attemptEdits, [questionNumber]: value };
    setAttemptEdits(nextEdits);
    attemptEditsRef.current = nextEdits;
    await saveAttemptEdits(nextEdits, questionNumber);
  }

  async function saveAttemptEdits(edits, singleQuestionNumber = null) {
    if (!attemptModal.detail) return;
    if (savingAttempt) {
      setPendingAttemptSave(true);
      return;
    }
    setSavingAttempt(true);
    setError('');
    try {
      const sourceRows = attemptModal.detail.answers;
      const answers = sourceRows
        .filter((row) => singleQuestionNumber === null || row.question_number === singleQuestionNumber)
        .map((row) => {
        const value = edits[row.question_number] ?? '';
        if (value === '') {
          return { question_number: row.question_number, manual_override: false, manual_answer: null };
        }
        if (value === '__blank__') {
          return { question_number: row.question_number, manual_override: true, manual_answer: null };
        }
        return { question_number: row.question_number, manual_override: true, manual_answer: value };
      });
      const updated = await updateOmrAttemptAnswers(attemptModal.detail.attempt_id, answers);
      setAttemptModal({ open: true, detail: updated });
      const nextEdits = {};
      updated.answers.forEach((answer) => {
        nextEdits[answer.question_number] = buildManualValue(answer);
      });
      setAttemptEdits(nextEdits);
      attemptEditsRef.current = nextEdits;
      refreshAttempts();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingAttempt(false);
      if (pendingAttemptSave) {
        setPendingAttemptSave(false);
        saveAttemptEdits(attemptEditsRef.current, null);
      }
    }
  }

  function handleSaveAttemptEdits() {
    return saveAttemptEdits(attemptEdits, null);
  }

  function handleViewAttemptImage(row) {
    if (!row.uploaded_image_path) return;
    const raw = String(row.uploaded_image_path);
    if (raw.startsWith('http://') || raw.startsWith('https://')) {
      setAttemptImage(raw);
      return;
    }
    if (raw.includes('/data/input/')) {
      const idx = raw.indexOf('/data/input/');
      const relative = raw.slice(idx + '/data/input/'.length);
      const base = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
      setAttemptImage(`${base}/assets/${relative}`);
      return;
    }
    const base = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
    if (raw.startsWith('/assets/')) {
      setAttemptImage(`${base}${raw}`);
      return;
    }
    if (raw.startsWith('assets/')) {
      setAttemptImage(`${base}/${raw}`);
      return;
    }
    if (raw.startsWith('data/input/')) {
      const relative = raw.replace(/^data\/input\//, '');
      setAttemptImage(`${base}/assets/${relative}`);
      return;
    }
    setAttemptImage(`${base}/assets/${raw}`);
  }

  function closeAttemptModal() {
    setAttemptModal({ open: false, detail: null });
    setAttemptEdits({});
    attemptEditsRef.current = {};
    setPendingAttemptSave(false);
  }

  function closeAttemptImage() {
    setAttemptImage(null);
  }

  const filteredItems = useMemo(() => filterItems(items, filters), [items, filters]);
  const filteredAttempts = useMemo(() => {
    const query = attemptFilters.query.trim().toLowerCase();
    return attempts.filter((row) => {
      if (attemptFilters.status && row.status !== attemptFilters.status) {
        return false;
      }
      if (attemptFilters.group && row.student_group !== attemptFilters.group) {
        return false;
      }
      if (!query) return true;
      const haystack = [
        row.exam_title,
        row.student_name,
        row.exam_id,
        row.exam_version_code,
        row.exam_code,
      ]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase())
        .join(' ');
      return haystack.includes(query);
    });
  }, [attempts, attemptFilters]);

  const attemptStatusOptions = useMemo(() => {
    const values = new Set();
    attempts.forEach((row) => {
      if (row.status) values.add(row.status);
    });
    return Array.from(values).sort();
  }, [attempts]);

  const attemptGroupOptions = useMemo(() => {
    const values = new Set();
    attempts.forEach((row) => {
      if (row.student_group) values.add(row.student_group);
    });
    return Array.from(values).sort();
  }, [attempts]);

  async function handleSelectItem(itemId) {
    setError('');
    setMessage('');
    try {
      const item = await getItem(itemId);
      setSelectedItemId(item.id);
      setForm(itemToForm(item));
      setActiveTab('edit');
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSubmit() {
    setSaving(true);
    setError('');
    setMessage('');
    try {
      if (!docHasMeaningfulContent(form.statement_doc)) {
        throw new Error('El enunciado no puede estar vacio');
      }
      if (!docHasMeaningfulContent(form.optionA_doc)) {
        throw new Error('La opcion A no puede estar vacia');
      }
      if (!docHasMeaningfulContent(form.optionB_doc)) {
        throw new Error('La opcion B no puede estar vacia');
      }
      if (!docHasMeaningfulContent(form.optionC_doc)) {
        throw new Error('La opcion C no puede estar vacia');
      }
      if (!docHasMeaningfulContent(form.optionD_doc)) {
        throw new Error('La opcion D no puede estar vacia');
      }

      const payload = formToPayload(form);
      if (selectedItemId) {
        await updateItem(selectedItemId, payload);
        setMessage(`Item #${selectedItemId} actualizado`);
      } else {
        const created = await createItem(payload);
        setMessage(`Item #${created.id} creado`);
      }
      await refreshItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  function handleReset() {
    setSelectedItemId(null);
    setForm(emptyForm());
    setActiveTab('edit');
    setMessage('Formulario reiniciado');
    setError('');
  }

  async function handleDeleteItem() {
    if (!selectedItemId) return;
    if (!window.confirm(`¿Borrar item #${selectedItemId}? Esta acción no se puede deshacer.`)) return;
    setSaving(true);
    setError('');
    setMessage('');
    try {
      await deleteItem(selectedItemId);
      setMessage(`Item #${selectedItemId} eliminado`);
      setSelectedItemId(null);
      setForm(emptyForm());
      await refreshItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }


  function handleToggleItemSelection(itemId, checked) {
    setSelectedItemIds((prev) => {
      if (checked) {
        if (prev.includes(itemId)) return prev;
        return [...prev, itemId];
      }
      return prev.filter((id) => id !== itemId);
    });
  }

  function handleToggleAllVisibleItems(itemIds, checked) {
    setSelectedItemIds((prev) => {
      const set = new Set(prev);
      if (checked) {
        itemIds.forEach((id) => set.add(id));
      } else {
        itemIds.forEach((id) => set.delete(id));
      }
      return Array.from(set);
    });
  }

  async function handleBulkDeleteItems(itemIds, force = false) {
    const ids = (itemIds || []).filter((id) => Number.isFinite(id));
    if (ids.length === 0) return;

    const ok = window.confirm(
      force
        ? `¿FORZAR borrado de ${ids.length} item(s)? Esto eliminara asociaciones con examenes/versiones y no se puede deshacer.`
        : `¿Borrar ${ids.length} item(s) seleccionados? Esta acción no se puede deshacer.`
    );
    if (!ok) return;

    setSaving(true);
    setError('');
    setMessage('');

    const failed = [];
    let deleted = 0;

    try {
      for (const id of ids) {
        try {
          await deleteItem(id, { force });
          deleted += 1;
        } catch (err) {
          failed.push({ id, error: parseDeleteErrorDetail(err?.message) });
        }
      }

      if (ids.includes(selectedItemId)) {
        setSelectedItemId(null);
        setForm(emptyForm());
      }

      await refreshItems();
      setSelectedItemIds((prev) => prev.filter((id) => !ids.includes(id)));

      if (failed.length > 0) {
        const failedRows = failed.map((f) => `#${f.id} (${f.error})`).join(', ');
        setError(`No se pudieron borrar ${failed.length} item(s): ${failedRows}`);
      }
      setMessage(force ? `Forzar borrado completado. Eliminados: ${deleted}.` : `Borrado masivo completado. Eliminados: ${deleted}.`);
    } finally {
      setSaving(false);
    }
  }

  function handleNavigate(direction) {
    const idx = items.findIndex((it) => it.id === selectedItemId);
    const nextIdx = idx + direction;
    if (nextIdx >= 0 && nextIdx < items.length) {
      handleSelectItem(items[nextIdx].id);
    }
  }

  async function refreshExams(teacherId) {
    setLoadingExams(true);
    setError('');
    try {
      const data = await listExams(teacherId);
      setExams(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingExams(false);
    }
  }

  async function handleCreateExam(formData) {
    setError('');
    setMessage('');
    const payload = {
      teacher_id: Number(formData.teacher_id),
      title: formData.title,
      description: formData.description || null,
    };
    const created = await createExam(payload);
    setMessage(`Examen #${created.id} creado`);
  }

  async function handleSelectExam(examId) {
    setError('');
    setMessage('');
    try {
      const detail = await getExam(examId);
      setSelectedExam(detail);
      const versions = await listExamVersions(examId);
      setExamVersions(versions);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAddItemToExam(examId, itemId) {
    setError('');
    setMessage('');
    try {
      const detail = await addItemToExam(examId, itemId);
      setSelectedExam(detail);
      setMessage(`Item #${itemId} asociado al examen #${examId}`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRemoveItemFromExam(examId, itemId) {
    setError('');
    setMessage('');
    try {
      const detail = await removeItemFromExam(examId, itemId);
      setSelectedExam(detail);
      setMessage(`Item #${itemId} removido del examen #${examId}`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handlePublishExamVersion(examId) {
    setError('');
    setMessage('');
    try {
      const versionCode = `V${String(examVersions.length + 1).padStart(3, '0')}`;
      const seed = Math.floor(Date.now() / 1000);
      await publishExamVersion(examId, {
        version_code: versionCode,
        seed_shuffle: seed,
        shuffle_questions: true,
        shuffle_options: true,
      });
      const versions = await listExamVersions(examId);
      setExamVersions(versions);
      setMessage(`Version ${versionCode} publicada`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleExportExamPdf(exam) {
    setError('');
    setMessage('');
    setExporting({ examId: exam.id, format: 'pdf' });
    try {
      const versions = await listExamVersions(exam.id);
      if (!versions.length) throw new Error('El examen no tiene versiones publicadas.');
      const latest = versions[versions.length - 1];
      await exportExamVersionPdf(
        exam.id,
        latest.id,
        `cuadernillo_exam_${exam.exam_code}_${latest.version_code}.pdf`
      );
      setMessage(`PDF descargado para examen #${exam.id} versión ${latest.version_code}.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting({ examId: null, format: null });
    }
  }

  async function handleExportExamDocx(exam) {
    setError('');
    setMessage('');
    setExporting({ examId: exam.id, format: 'docx' });
    try {
      const versions = await listExamVersions(exam.id);
      if (!versions.length) throw new Error('El examen no tiene versiones publicadas.');
      const latest = versions[versions.length - 1];
      await exportExamVersionDocx(
        exam.id,
        latest.id,
        `cuadernillo_exam_${exam.exam_code}_${latest.version_code}.docx`
      );
      setMessage(`DOCX descargado para examen #${exam.id} versión ${latest.version_code}.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting({ examId: null, format: null });
    }
  }

  async function handleViewVersionAnswerKey(exam, version) {
    setError('');
    setMessage('');
    setLoadingAnswerKey(true);
    try {
      const detail = await getExamVersion(exam.id, version.id);
      const rows = (detail.items || [])
        .map((row) => ({
          question_number: row.question_number,
          correct_answer: row.correct_answer_mapped,
          item_id: row.item_id,
        }))
        .sort((a, b) => a.question_number - b.question_number);

      setAnswerKeyModal({
        open: true,
        exam,
        version,
        rows,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAnswerKey(false);
    }
  }

  function handleCloseAnswerKeyModal() {
    setAnswerKeyModal({
      open: false,
      exam: null,
      version: null,
      rows: [],
    });
  }

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <h2>OMR Suite</h2>
        <button
          type="button"
          className={activeTab === 'edit' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('edit')}
        >
          Editar item
        </button>
        <button
          type="button"
          className={activeTab === 'list' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('list')}
        >
          Listado ({items.length})
        </button>
        <button
          type="button"
          className={activeTab === 'exam' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('exam')}
        >
          Armado de examen
        </button>
        <button
          type="button"
          className={activeTab === 'graded' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('graded')}
        >
          Examenes calificados
        </button>
        <button
          type="button"
          className={activeTab === 'students' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('students')}
        >
          Estudiantes
        </button>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-topbar card">
          <div>
            <h1>Banco de Items</h1>
            <p>API: {API_BASE_URL}</p>
          </div>
        </header>

        {error ? <p className="alert error">{error}</p> : null}
        {message ? <p className="alert success">{message}</p> : null}

        {activeTab === 'edit' ? (
          <section className="single-pane">
            <ItemForm
              form={form}
              onChange={setForm}
              onSubmit={handleSubmit}
              onReset={handleReset}
              onDelete={handleDeleteItem}
              onNavigatePrev={() => handleNavigate(-1)}
              onNavigateNext={() => handleNavigate(1)}
              hasPrev={items.findIndex((it) => it.id === selectedItemId) > 0}
              hasNext={items.findIndex((it) => it.id === selectedItemId) < items.length - 1}
              isSaving={saving}
              mode={selectedItemId ? 'edit' : 'create'}
            />
          </section>
        ) : null}

        {activeTab === 'list' ? (
          <section className="single-pane">
            <FiltersBar
              filters={filters}
              onChange={setFilters}
              onClear={() => setFilters({ subject: '', difficulty: '', curricularTag: '' })}
            />
            {loading ? <p>Cargando items...</p> : null}
            <ItemList
              items={filteredItems}
              selectedItemId={selectedItemId}
              onSelect={handleSelectItem}
              selectedItemIds={selectedItemIds}
              onToggleItemSelection={handleToggleItemSelection}
              onToggleAllVisibleItems={handleToggleAllVisibleItems}
              onBulkDelete={(ids) => handleBulkDeleteItems(ids, false)}
              onBulkForceDelete={(ids) => handleBulkDeleteItems(ids, true)}
              isBulkDeleting={saving}
            />
          </section>
        ) : null}

        {activeTab === 'exam' ? (
          <ExamBuilder
            items={items}
            exams={exams}
            selectedExam={selectedExam}
            versions={examVersions}
            onRefreshExams={refreshExams}
            onCreateExam={handleCreateExam}
            onSelectExam={handleSelectExam}
            onAddItem={handleAddItemToExam}
            onRemoveItem={handleRemoveItemFromExam}
            onPublishVersion={handlePublishExamVersion}
            onExportExamPdf={handleExportExamPdf}
            onExportExamDocx={handleExportExamDocx}
            onViewVersionAnswerKey={handleViewVersionAnswerKey}
            answerKeyModal={answerKeyModal}
            onCloseAnswerKeyModal={handleCloseAnswerKeyModal}
            exporting={exporting}
            loadingAnswerKey={loadingAnswerKey}
            loading={loadingExams}
          />
        ) : null}

        {activeTab === 'students' ? (
          <section className="single-pane">
            {loadingStudents ? <p>Cargando estudiantes...</p> : null}
            <section className="card">
              <h3>Filtros</h3>
              <div className="grid grid-3">
                <label>
                  Buscar (nombre, correo, documento, UUID)
                  <input
                    value={studentFilters.query}
                    onChange={(e) => setStudentFilters({ ...studentFilters, query: e.target.value })}
                    placeholder="Ej: maria, 1032, @cevu.edu.co"
                  />
                </label>
                <label>
                  Grupo
                  <input
                    value={studentFilters.group}
                    onChange={(e) => setStudentFilters({ ...studentFilters, group: e.target.value })}
                    placeholder="Ej: 11A2026"
                  />
                </label>
                <label>
                  Ordenar por
                  <select
                    value={studentSortKey}
                    onChange={(e) => setStudentSortKey(e.target.value)}
                  >
                    <option value="id_asc">ID (asc)</option>
                    <option value="id_desc">ID (desc)</option>
                    <option value="apellido_asc">Apellido (A-Z)</option>
                    <option value="apellido_desc">Apellido (Z-A)</option>
                    <option value="grupo_asc">Grupo (A-Z)</option>
                    <option value="grupo_desc">Grupo (Z-A)</option>
                    <option value="documento_asc">Documento (asc)</option>
                    <option value="documento_desc">Documento (desc)</option>
                  </select>
                </label>
              </div>
              <button
                type="button"
                onClick={() => {
                  setStudentFilters({ query: '', group: '' });
                  setStudentSortKey('id_asc');
                }}
              >
                Limpiar filtros
              </button>
            </section>
            <StudentList students={students} filters={studentFilters} sortKey={studentSortKey} />
          </section>
        ) : null}

        {activeTab === 'graded' ? (
          <section className="single-pane">
            {loadingAttempts ? <p>Cargando intentos...</p> : null}
            <AttemptList
              attempts={filteredAttempts}
              filters={attemptFilters}
              statusOptions={attemptStatusOptions}
              groupOptions={attemptGroupOptions}
              onFilterChange={setAttemptFilters}
              onView={handleViewAttempt}
              onViewImage={handleViewAttemptImage}
            />
          </section>
        ) : null}
      </main>
      {exporting.examId ? (
        <div className="loading-overlay" role="status" aria-live="polite">
          <div className="loading-card">
            <div className="loading-spinner" />
            <p>
              Generando exportación {exporting.format?.toUpperCase()} del examen #{exporting.examId}...
            </p>
          </div>
        </div>
      ) : null}

      {attemptModal.open && attemptModal.detail ? (
        <div className="preview-modal-overlay" onClick={closeAttemptModal}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Intento #{attemptModal.detail.attempt_id}</h4>
              <button type="button" onClick={closeAttemptModal}>Cerrar</button>
            </div>
            <p className="helper-text">
              Examen #{attemptModal.detail.exam_id} | Version {attemptModal.detail.exam_version_id || '-'} | Estado {attemptModal.detail.status}
            </p>
            <div className="modal-actions">
              <button type="button" onClick={handleSaveAttemptEdits} disabled={savingAttempt}>
                {savingAttempt ? 'Guardando...' : 'Guardar ahora'}
              </button>
              <span className="helper-text">Los cambios se guardan automaticamente al cambiar el selector.</span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Pregunta</th>
                    <th>Correcta</th>
                    <th>Detectada</th>
                    <th>Correccion</th>
                    <th>Final</th>
                  </tr>
                </thead>
                <tbody>
                  {attemptModal.detail.answers.map((row) => (
                    <tr key={row.question_number}>
                      <td>{row.question_number}</td>
                      <td>{row.correct_answer || '-'}</td>
                      <td>{row.marked_answer || '-'}</td>
                      <td>
                        <select
                          value={attemptEdits[row.question_number] ?? ''}
                          onChange={(e) => handleAttemptEditChange(row.question_number, e.target.value)}
                        >
                          <option value="">Sin override</option>
                          <option value="__blank__">Forzar blanco</option>
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                          <option value="D">D</option>
                        </select>
                      </td>
                      <td className="final-status-cell">
                        <span className="final-answer">{row.effective_answer || '-'}</span>
                        <span
                          className={[
                            'status-icon',
                            row.effective_status === 'correct'
                              ? 'status-correct'
                              : row.effective_status === 'incorrect'
                                ? 'status-incorrect'
                                : row.effective_status === 'blank'
                                  ? 'status-blank'
                                  : 'status-ambiguous',
                          ].join(' ')}
                          title={row.effective_status}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}

      {attemptImage ? (
        <div className="preview-modal-overlay" onClick={closeAttemptImage}>
          <div className="preview-modal image-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Imagen del examen</h4>
              <button type="button" onClick={closeAttemptImage}>Cerrar</button>
            </div>
            <img src={attemptImage} alt="omr" style={{ width: '100%', borderRadius: 8 }} />
          </div>
        </div>
      ) : null}
    </div>
  );
}
