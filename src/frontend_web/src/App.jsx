import { useEffect, useMemo, useState } from 'react';

import { createItem, getItem, listItems, updateItem, API_BASE_URL } from './api/itemsApi';
import {
  addItemToExam,
  createExam,
  getExam,
  listExams,
  listExamVersions,
  publishExamVersion,
  removeItemFromExam,
} from './api/examsApi';
import ExamBuilder from './components/ExamBuilder';
import FiltersBar from './components/FiltersBar';
import ItemForm, { emptyForm, formToPayload, itemToForm } from './components/ItemForm';
import ItemList from './components/ItemList';
import { docToPlainText } from './utils/editorDoc';

function filterItems(items, filters) {
  const subject = filters.subject.trim().toLowerCase();
  const difficulty = filters.difficulty.trim().toLowerCase();
  const curricularTag = filters.curricularTag.trim().toLowerCase();

  return items.filter((item) => {
    if (subject && !(item.subject || '').toLowerCase().includes(subject)) return false;
    if (difficulty && !(item.difficulty || '').toLowerCase().includes(difficulty)) return false;

    if (curricularTag) {
      const label = `${item.curriculum?.standard_code || ''} ${item.curriculum?.competency_code || ''}`.toLowerCase();
      if (!label.includes(curricularTag)) return false;
    }

    return true;
  });
}

export default function App() {
  const [items, setItems] = useState([]);
  const [selectedItemId, setSelectedItemId] = useState(null);
  const [form, setForm] = useState(emptyForm());
  const [filters, setFilters] = useState({ subject: '', difficulty: '', curricularTag: '' });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingExams, setLoadingExams] = useState(false);
  const [exams, setExams] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);
  const [examVersions, setExamVersions] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

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

  useEffect(() => {
    refreshItems();
  }, []);

  const filteredItems = useMemo(() => filterItems(items, filters), [items, filters]);

  async function handleSelectItem(itemId) {
    setError('');
    setMessage('');
    try {
      const item = await getItem(itemId);
      setSelectedItemId(item.id);
      setForm(itemToForm(item));
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSubmit() {
    setSaving(true);
    setError('');
    setMessage('');
    try {
      if (!docToPlainText(form.statement_doc)) {
        throw new Error('El enunciado no puede estar vacio');
      }
      if (!docToPlainText(form.optionA_doc)) {
        throw new Error('La opcion A no puede estar vacia');
      }
      if (!docToPlainText(form.optionB_doc)) {
        throw new Error('La opcion B no puede estar vacia');
      }
      if (!docToPlainText(form.optionC_doc)) {
        throw new Error('La opcion C no puede estar vacia');
      }
      if (!docToPlainText(form.optionD_doc)) {
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
    setMessage('Formulario reiniciado');
    setError('');
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
      exam_code: formData.exam_code,
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

  return (
    <main className="container">
      <header>
        <h1>Banco de Items - Frontend Web Base</h1>
        <p>API: {API_BASE_URL}</p>
      </header>

      {error ? <p className="alert error">{error}</p> : null}
      {message ? <p className="alert success">{message}</p> : null}

      <FiltersBar
        filters={filters}
        onChange={setFilters}
        onClear={() => setFilters({ subject: '', difficulty: '', curricularTag: '' })}
      />

      <section className="layout">
        <ItemForm
          form={form}
          onChange={setForm}
          onSubmit={handleSubmit}
          onReset={handleReset}
          isSaving={saving}
          mode={selectedItemId ? 'edit' : 'create'}
        />

        <div>
          {loading ? <p>Cargando items...</p> : null}
          <ItemList items={filteredItems} selectedItemId={selectedItemId} onSelect={handleSelectItem} />
        </div>
      </section>

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
        loading={loadingExams}
      />
    </main>
  );
}
