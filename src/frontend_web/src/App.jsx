import { useEffect, useMemo, useRef, useState } from 'react';

import { createItem, deleteItem, getItem, listItems, updateItem, API_BASE_URL } from './api/itemsApi';
import { listStudents } from './api/studentsApi';
import {
  getOmrAttempt,
  deleteOmrAttempt,
  listOmrAttempts,
  updateOmrAttemptAnswers,
  getOmrAttemptRatios,
  getOmrAttemptOverlay,
  assignOmrAttempt,
  getOmrThresholds,
  updateOmrThresholds,
} from './api/omrApi';
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
  const [attemptRatios, setAttemptRatios] = useState({ open: false, detail: null });
  const [attemptOverlay, setAttemptOverlay] = useState({ open: false, detail: null, image: null });
  const [assignExamId, setAssignExamId] = useState('');
  const [assignExamCode, setAssignExamCode] = useState('');
  const [assignVersionId, setAssignVersionId] = useState('');
  const [assignStudentId, setAssignStudentId] = useState('');
  const [assignStudentQuery, setAssignStudentQuery] = useState('');
  const [assignDocumentNumber, setAssignDocumentNumber] = useState('');
  const [assigningAttempt, setAssigningAttempt] = useState(false);
  const [attemptEdits, setAttemptEdits] = useState({});
  const [savingAttempt, setSavingAttempt] = useState(false);
  const [pendingAttemptSave, setPendingAttemptSave] = useState(false);
  const attemptEditsRef = useRef({});
  const [attemptFilters, setAttemptFilters] = useState({ query: '', status: '', group: '' });
  const [omrThresholds, setOmrThresholds] = useState({ marked: '0.32', unmarked: '0.30' });
  const [savingThresholds, setSavingThresholds] = useState(false);
  const [selectedAttemptIds, setSelectedAttemptIds] = useState([]);
  const [deletingAttemptIds, setDeletingAttemptIds] = useState([]);
  const [deletingSelectedAttempts, setDeletingSelectedAttempts] = useState(false);

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
      refreshThresholds();
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

  useEffect(() => {
    const availableIds = new Set(attempts.map((row) => row.attempt_id));
    setSelectedAttemptIds((prev) => prev.filter((attemptId) => availableIds.has(attemptId)));
  }, [attempts]);

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

  async function refreshThresholds() {
    setError('');
    try {
      const data = await getOmrThresholds();
      setOmrThresholds({
        marked: String(data.marked ?? ''),
        unmarked: String(data.unmarked ?? ''),
      });
    } catch (err) {
      setError(err.message);
    }
  }

  function buildManualValue(row) {
    if (row.manual_override) {
      return row.manual_answer ? row.manual_answer : '__blank__';
    }
    return '';
  }

  function formatStudentOption(student) {
    return `${student.document_number} - ${student.first_name} ${student.last_name}`;
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
      const teacherId = detail.teacher_id || 1;
      if (exams.length === 0) {
        const data = await listExams(teacherId);
        setExams(data);
      }
      if (students.length === 0) {
        const data = await listStudents({ limit: 500 });
        setStudents(data);
      }
      if (detail.exam_id) {
        setAssignExamId(String(detail.exam_id));
        const versions = await listExamVersions(detail.exam_id);
        setExamVersions(versions);
        setAssignVersionId(detail.exam_version_id ? String(detail.exam_version_id) : '');
      } else {
        setAssignExamId('');
        setAssignVersionId('');
      }
      setAssignExamCode(detail.exam_code_detected || '');
      setAssignStudentId(detail.student?.id ? String(detail.student.id) : '');
      if (detail.student?.id && detail.student?.document_number) {
        setAssignStudentQuery(
          `${detail.student.document_number} - ${detail.student.first_name || ''} ${detail.student.last_name || ''}`.trim()
        );
      } else {
        setAssignStudentQuery('');
      }
      setAssignDocumentNumber(detail.student?.document_number || '');
    } catch (err) {
      setError(err.message);
    }
  }

  function handleToggleAttemptSelection(attemptId, checked) {
    setSelectedAttemptIds((prev) => {
      if (checked) {
        return prev.includes(attemptId) ? prev : [...prev, attemptId];
      }
      return prev.filter((id) => id !== attemptId);
    });
  }

  function handleToggleAllAttemptSelection(checked) {
    const visibleIds = filteredAttempts.map((row) => row.attempt_id);
    setSelectedAttemptIds((prev) => {
      if (!checked) {
        return prev.filter((id) => !visibleIds.includes(id));
      }
      const next = new Set(prev);
      visibleIds.forEach((id) => next.add(id));
      return Array.from(next);
    });
  }

  function clearDeletedAttemptsFromUi(attemptIds) {
    const deleted = new Set(attemptIds);
    setAttempts((prev) => prev.filter((row) => !deleted.has(row.attempt_id)));
    setSelectedAttemptIds((prev) => prev.filter((id) => !deleted.has(id)));
    if (attemptModal.detail && deleted.has(attemptModal.detail.attempt_id)) {
      closeAttemptModal();
    }
    if (attemptRatios.detail && deleted.has(attemptRatios.detail.attempt_id)) {
      closeAttemptRatios();
    }
    if (attemptOverlay.detail && deleted.has(attemptOverlay.detail.attempt_id)) {
      closeAttemptOverlay();
    }
  }

  async function handleDeleteAttempt(row) {
    const confirmed = window.confirm(`Borrar el intento #${row.attempt_id}? Esta accion quita el registro de examenes calificados.`);
    if (!confirmed) return;
    setDeletingAttemptIds((prev) => (prev.includes(row.attempt_id) ? prev : [...prev, row.attempt_id]));
    setError('');
    setMessage('');
    try {
      await deleteOmrAttempt(row.attempt_id);
      clearDeletedAttemptsFromUi([row.attempt_id]);
      setMessage(`Intento #${row.attempt_id} borrado.`);
      refreshAttempts();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingAttemptIds((prev) => prev.filter((id) => id !== row.attempt_id));
    }
  }

  async function handleDeleteSelectedAttempts() {
    const ids = selectedAttemptIds.filter((id) => attempts.some((row) => row.attempt_id === id));
    if (ids.length === 0) return;
    const confirmed = window.confirm(`Borrar ${ids.length} intento${ids.length === 1 ? '' : 's'} seleccionado${ids.length === 1 ? '' : 's'}?`);
    if (!confirmed) return;
    setDeletingSelectedAttempts(true);
    setDeletingAttemptIds((prev) => Array.from(new Set([...prev, ...ids])));
    setError('');
    setMessage('');
    try {
      await Promise.all(ids.map((attemptId) => deleteOmrAttempt(attemptId)));
      clearDeletedAttemptsFromUi(ids);
      setMessage(`${ids.length} intento${ids.length === 1 ? '' : 's'} borrado${ids.length === 1 ? '' : 's'}.`);
      refreshAttempts();
    } catch (err) {
      setError(err.message);
      refreshAttempts();
    } finally {
      setDeletingSelectedAttempts(false);
      setDeletingAttemptIds((prev) => prev.filter((id) => !ids.includes(id)));
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

  function mapAssetUrl(pathValue) {
    if (!pathValue) return null;
    const raw = String(pathValue);
    if (raw.startsWith('http://') || raw.startsWith('https://')) {
      return raw;
    }
    if (raw.includes('/data/input/')) {
      const idx = raw.indexOf('/data/input/');
      const relative = raw.slice(idx + '/data/input/'.length);
      const base = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
      return `${base}/assets/${relative}`;
    }
    const base = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
    if (raw.startsWith('/assets/')) {
      return `${base}${raw}`;
    }
    if (raw.startsWith('assets/')) {
      return `${base}/${raw}`;
    }
    if (raw.startsWith('data/input/')) {
      const relative = raw.replace(/^data\/input\//, '');
      return `${base}/assets/${relative}`;
    }
    return `${base}/assets/${raw}`;
  }

  function handleViewAttemptImage(row) {
    if (!row.uploaded_image_path) return;
    const mapped = mapAssetUrl(row.uploaded_image_path);
    if (mapped) setAttemptImage(mapped);
  }

  async function handleViewAttemptRatios(row) {
    setError('');
    try {
      const detail = await getOmrAttemptRatios(row.attempt_id);
      setAttemptRatios({ open: true, detail });
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleViewAttemptOverlay(row) {
    setError('');
    try {
      const detail = await getOmrAttemptOverlay(row.attempt_id);
      const mapped = mapAssetUrl(detail.aligned_image_path);
      setAttemptOverlay({ open: true, detail, image: mapped });
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAssignExamChange(value) {
    setAssignExamId(value);
    setAssignVersionId('');
    if (!value) {
      setExamVersions([]);
      return;
    }
    try {
      const versions = await listExamVersions(Number(value));
      setExamVersions(versions);
    } catch (err) {
      setError(err.message);
    }
  }

  function handleAssignStudentQueryChange(value) {
    setAssignStudentQuery(value);
    const normalized = value.trim().toLowerCase();
    if (!normalized) {
      setAssignStudentId('');
      return;
    }
    const matched = students.find((student) => formatStudentOption(student).toLowerCase() === normalized);
    if (matched) {
      setAssignStudentId(String(matched.id));
      setAssignDocumentNumber(matched.document_number || '');
      return;
    }
    setAssignStudentId('');
  }

  async function handleApplyAssignment() {
    if (!attemptModal.detail) return;
    setAssigningAttempt(true);
    setError('');
    try {
      const payload = {
        exam_id: assignExamId ? Number(assignExamId) : null,
        exam_code: assignExamCode || null,
        exam_version_id: assignVersionId ? Number(assignVersionId) : null,
        student_id: assignStudentId ? Number(assignStudentId) : null,
        document_number: assignDocumentNumber || null,
      };
      const updated = await assignOmrAttempt(attemptModal.detail.attempt_id, payload);
      setAttemptModal({ open: true, detail: updated });
      refreshAttempts();
    } catch (err) {
      setError(err.message);
    } finally {
      setAssigningAttempt(false);
    }
  }

  function closeAttemptModal() {
    setAttemptModal({ open: false, detail: null });
    setAttemptEdits({});
    attemptEditsRef.current = {};
    setPendingAttemptSave(false);
    setAssignExamId('');
    setAssignExamCode('');
    setAssignVersionId('');
    setAssignStudentId('');
    setAssignStudentQuery('');
    setAssignDocumentNumber('');
  }

  function closeAttemptImage() {
    setAttemptImage(null);
  }

  function closeAttemptRatios() {
    setAttemptRatios({ open: false, detail: null });
  }

  function closeAttemptOverlay() {
    setAttemptOverlay({ open: false, detail: null, image: null });
  }

  function handleThresholdChange(field, value) {
    setOmrThresholds((prev) => ({ ...prev, [field]: value }));
  }

  async function handleThresholdBlur() {
    const marked = Number(omrThresholds.marked);
    const unmarked = Number(omrThresholds.unmarked);
    if (Number.isNaN(marked) || Number.isNaN(unmarked)) {
      setError('Los umbrales deben ser numéricos.');
      return;
    }
    setSavingThresholds(true);
    setError('');
    try {
      const data = await updateOmrThresholds({ marked, unmarked });
      setOmrThresholds({
        marked: String(data.marked),
        unmarked: String(data.unmarked),
      });
      setMessage(`Umbrales actualizados: marcada=${data.marked}, no marcada=${data.unmarked}`);
    } catch (err) {
      setError(err.message);
      refreshThresholds();
    } finally {
      setSavingThresholds(false);
    }
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
      const seed = Math.floor(Date.now() / 1000);
      const published = await publishExamVersion(examId, {
        seed_shuffle: seed,
        shuffle_questions: true,
        shuffle_options: true,
      });
      const versions = await listExamVersions(examId);
      setExamVersions(versions);
      setMessage(`Version ${published.version_code} publicada`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleExportExamPdf(exam, version) {
    setError('');
    setMessage('');
    setExporting({ examId: exam.id, format: 'pdf' });
    try {
      await exportExamVersionPdf(
        exam.id,
        version.id,
        `cuadernillo_exam_${version.exam_code}_${version.version_code}.pdf`
      );
      setMessage(`PDF descargado para examen #${exam.id} código ${version.exam_code} versión ${version.version_code}.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting({ examId: null, format: null });
    }
  }

  async function handleExportExamDocx(exam, version) {
    setError('');
    setMessage('');
    setExporting({ examId: exam.id, format: 'docx' });
    try {
      await exportExamVersionDocx(
        exam.id,
        version.id,
        `cuadernillo_exam_${version.exam_code}_${version.version_code}.docx`
      );
      setMessage(`DOCX descargado para examen #${exam.id} código ${version.exam_code} versión ${version.version_code}.`);
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
              thresholds={omrThresholds}
              savingThresholds={savingThresholds}
              onFilterChange={setAttemptFilters}
              onThresholdChange={handleThresholdChange}
              onThresholdBlur={handleThresholdBlur}
              onView={handleViewAttempt}
              onViewImage={handleViewAttemptImage}
              onViewRatios={handleViewAttemptRatios}
              onViewOverlay={handleViewAttemptOverlay}
              selectedAttemptIds={selectedAttemptIds}
              deletingAttemptIds={deletingAttemptIds}
              deletingSelected={deletingSelectedAttempts}
              onToggleAttemptSelection={handleToggleAttemptSelection}
              onToggleAllAttempts={handleToggleAllAttemptSelection}
              onDelete={handleDeleteAttempt}
              onDeleteSelected={handleDeleteSelectedAttempts}
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
            <div className="assign-grid">
              <label>
                Examen (selector)
                <select value={assignExamId} onChange={(e) => handleAssignExamChange(e.target.value)}>
                  <option value="">Selecciona examen</option>
                  {exams.map((exam) => (
                    <option key={exam.id} value={exam.id}>
                      {exam.exam_code} - {exam.title}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Version
                <select value={assignVersionId} onChange={(e) => setAssignVersionId(e.target.value)}>
                  <option value="">Ultima version</option>
                  {examVersions.map((version) => (
                    <option key={version.id} value={version.id}>
                      {version.version_code}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Exam code (manual)
                <input
                  type="text"
                  value={assignExamCode}
                  onChange={(e) => setAssignExamCode(e.target.value)}
                  placeholder="Ej: 1"
                />
              </label>
              <label>
                Estudiante (autocompletar)
                <input
                  type="text"
                  list="students-attempt-assign-list"
                  value={assignStudentQuery}
                  onChange={(e) => handleAssignStudentQueryChange(e.target.value)}
                  placeholder="Busca por documento o nombre"
                />
                <datalist id="students-attempt-assign-list">
                  {students.map((student) => (
                    <option key={student.id} value={formatStudentOption(student)} />
                  ))}
                </datalist>
              </label>
              <label>
                Documento (manual)
                <input
                  type="text"
                  value={assignDocumentNumber}
                  onChange={(e) => setAssignDocumentNumber(e.target.value)}
                  placeholder="Documento"
                />
              </label>
              <button type="button" onClick={handleApplyAssignment} disabled={assigningAttempt}>
                {assigningAttempt ? 'Asignando...' : 'Aplicar asignacion'}
              </button>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Pregunta</th>
                    <th>Detectada</th>
                    <th>Correcta</th>
                    <th>Correccion</th>
                    <th>Final</th>
                  </tr>
                </thead>
                <tbody>
                  {attemptModal.detail.answers.map((row) => (
                    <tr
                      key={row.question_number}
                      className={!row.marked_answer ? 'row-unmarked' : undefined}
                    >
                      <td>{row.question_number}</td>
                      <td>{row.marked_answer || '-'}</td>
                      <td>{row.correct_answer || '-'}</td>
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

      {attemptRatios.open && attemptRatios.detail ? (
        <div className="preview-modal-overlay" onClick={closeAttemptRatios}>
          <div className="preview-modal ratios-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Ratios lectura OMR</h4>
              <button type="button" onClick={closeAttemptRatios}>Cerrar</button>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Pregunta</th>
                    <th>A</th>
                    <th>B</th>
                    <th>C</th>
                    <th>D</th>
                    <th>Top1</th>
                    <th>Top2</th>
                    <th>Margin</th>
                    <th>Marcadas</th>
                    <th>Ambiguas</th>
                  </tr>
                </thead>
                <tbody>
                  {attemptRatios.detail.question_ratios.map((row) => (
                    <tr key={row.question_number}>
                      <td>{row.question_number}</td>
                      <td>{row.ratios?.A ?? '-'}</td>
                      <td>{row.ratios?.B ?? '-'}</td>
                      <td>{row.ratios?.C ?? '-'}</td>
                      <td>{row.ratios?.D ?? '-'}</td>
                      <td>
                        {row.top1_label || '-'} {row.top1_ratio ? `(${row.top1_ratio})` : ''}
                      </td>
                      <td>
                        {row.top2_label || '-'} {row.top2_ratio ? `(${row.top2_ratio})` : ''}
                      </td>
                      <td>{row.margin ?? '-'}</td>
                      <td>{row.marked_options || '-'}</td>
                      <td>{row.ambiguous_options || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <details className="ratios-details">
              <summary>Ratios auxiliares</summary>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      {attemptRatios.detail.auxiliary_ratios[0]
                        ? Object.keys(attemptRatios.detail.auxiliary_ratios[0]).map((key) => (
                            <th key={key}>{key}</th>
                          ))
                        : null}
                    </tr>
                  </thead>
                  <tbody>
                    {attemptRatios.detail.auxiliary_ratios.map((row, idx) => {
                      const fillRatio = Number(row.fill_ratio);
                      const top1Ratio = Number(row.top1_ratio);
                      const highlightTop =
                        Number.isFinite(fillRatio) &&
                        Number.isFinite(top1Ratio) &&
                        Math.abs(fillRatio - top1Ratio) < 1e-6;
                      return (
                        <tr key={idx} className={highlightTop ? 'row-top-ratio' : undefined}>
                          {Object.values(row).map((value, colIdx) => (
                            <td key={colIdx}>{value}</td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </details>
          </div>
        </div>
      ) : null}

      {attemptOverlay.open && attemptOverlay.detail ? (
        <div className="preview-modal-overlay" onClick={closeAttemptOverlay}>
          <div className="preview-modal overlay-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h4>Overlay respuestas</h4>
              <button type="button" onClick={closeAttemptOverlay}>Cerrar</button>
            </div>
            {!attemptOverlay.image ? (
              <p className="helper-text">No hay imagen alineada disponible.</p>
            ) : (
              <div className="overlay-container">
                <img className="overlay-image" src={attemptOverlay.image} alt="omr aligned" />
                <svg
                  className="overlay-svg"
                  viewBox={`0 0 ${attemptOverlay.detail.page_width_px || 1} ${attemptOverlay.detail.page_height_px || 1}`}
                  preserveAspectRatio="xMidYMid meet"
                >
                  {attemptOverlay.detail.questions.flatMap((question) =>
                    question.options
                      .filter((option) => option.is_correct || option.is_effective)
                      .map((option) => {
                        const size = option.r * 2.6;
                        const x = option.cx - size / 2;
                        const y = option.cy - size / 2;
                        const color = option.is_correct ? '#1b7d3a' : '#b81d1d';
                        return (
                          <rect
                            key={`${question.question_number}-${option.label}-${color}`}
                            x={x}
                            y={y}
                            width={size}
                            height={size}
                            fill="none"
                            stroke={color}
                            strokeWidth={6}
                          />
                        );
                      })
                  )}
                </svg>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
