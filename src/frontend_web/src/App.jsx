import { useEffect, useMemo, useState } from 'react';

import { createItem, getItem, listItems, updateItem, API_BASE_URL } from './api/itemsApi';
import FiltersBar from './components/FiltersBar';
import ItemForm, { emptyForm, formToPayload, itemToForm } from './components/ItemForm';
import ItemList from './components/ItemList';

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
      const payload = formToPayload(form);
      if (selectedItemId) {
        await updateItem(selectedItemId, {
          ...payload,
          teacher_id: undefined,
        });
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
    </main>
  );
}
