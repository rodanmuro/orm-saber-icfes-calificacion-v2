import { useEffect, useMemo, useState } from 'react';

import RichTextEditor from './RichTextEditor';
import { listCurriculumCompetencies, listCurriculumStandards } from '../api/itemsApi';
import { docToStorage, emptyDoc, storageToDoc } from '../utils/editorDoc';

const EMPTY_FORM = {
  id: null,
  teacher_id: 1,
  statement_doc: emptyDoc(),
  optionA_doc: emptyDoc(),
  optionB_doc: emptyDoc(),
  optionC_doc: emptyDoc(),
  optionD_doc: emptyDoc(),
  correct_answer: 'A',
  subject: '',
  difficulty: '',
  standard_id: null,
  standard_code: '',
  standard_name: '',
  competency_id: null,
  competency_code: '',
  competency_name: '',
};

export function itemToForm(item) {
  if (!item) return EMPTY_FORM;
  return {
    id: item.id,
    teacher_id: item.teacher_id,
    statement_doc: storageToDoc(item.statement),
    optionA_doc: storageToDoc(item.options?.A),
    optionB_doc: storageToDoc(item.options?.B),
    optionC_doc: storageToDoc(item.options?.C),
    optionD_doc: storageToDoc(item.options?.D),
    correct_answer: item.correct_answer || 'A',
    subject: item.subject || '',
    difficulty: item.difficulty || '',
    standard_id: item.curriculum?.standard_id || null,
    standard_code: item.curriculum?.standard_code || '',
    standard_name: item.curriculum?.standard_name || '',
    competency_id: item.curriculum?.competency_id || null,
    competency_code: item.curriculum?.competency_code || '',
    competency_name: item.curriculum?.competency_name || '',
  };
}

export function emptyForm() {
  return { ...EMPTY_FORM };
}

export function formToPayload(form) {
  const curriculum =
    form.standard_code || form.standard_name || form.competency_code || form.competency_name
      ? {
          standard_id: form.standard_id || null,
          standard_code: form.standard_code || null,
          standard_name: form.standard_name || null,
          competency_id: form.competency_id || null,
          competency_code: form.competency_code || null,
          competency_name: form.competency_name || null,
        }
      : null;

  return {
    teacher_id: Number(form.teacher_id),
    statement: docToStorage(form.statement_doc),
    options: {
      A: docToStorage(form.optionA_doc),
      B: docToStorage(form.optionB_doc),
      C: docToStorage(form.optionC_doc),
      D: docToStorage(form.optionD_doc),
    },
    correct_answer: form.correct_answer,
    subject: form.subject || null,
    difficulty: form.difficulty || null,
    curriculum,
  };
}

export default function ItemForm({ form, onChange, onSubmit, onReset, onDelete, onNavigatePrev, onNavigateNext, hasPrev, hasNext, isSaving, mode }) {
  const title = useMemo(() => (mode === 'edit' ? `Editar item #${form.id}` : 'Nuevo item'), [mode, form.id]);
  const [standardOptions, setStandardOptions] = useState([]);
  const [competencyOptions, setCompetencyOptions] = useState([]);

  useEffect(() => {
    let cancelled = false;
    const query = [form.standard_code, form.standard_name].filter(Boolean).join(' ').trim();
    listCurriculumStandards(query)
      .then((rows) => {
        if (!cancelled) setStandardOptions(rows);
      })
      .catch(() => {
        if (!cancelled) setStandardOptions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [form.standard_code, form.standard_name]);

  useEffect(() => {
    let cancelled = false;
    if (!form.standard_id && !form.standard_code) {
      setCompetencyOptions([]);
      return () => {
        cancelled = true;
      };
    }
    const query = [form.competency_code, form.competency_name].filter(Boolean).join(' ').trim();
    listCurriculumCompetencies({
      standardId: form.standard_id,
      standardCode: form.standard_code,
      query,
    })
      .then((rows) => {
        if (!cancelled) setCompetencyOptions(rows);
      })
      .catch(() => {
        if (!cancelled) setCompetencyOptions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [form.standard_id, form.standard_code, form.competency_code, form.competency_name]);

  function handleStandardCodeChange(value) {
    const match = standardOptions.find((row) => row.code === value);
    onChange({
      ...form,
      standard_id: match?.id || null,
      standard_code: value,
      standard_name: match?.name || form.standard_name,
      competency_id: null,
      competency_code: '',
      competency_name: '',
    });
  }

  function handleCompetencyCodeChange(value) {
    const match = competencyOptions.find((row) => row.code === value);
    onChange({
      ...form,
      competency_id: match?.id || null,
      competency_code: value,
      competency_name: match?.name || form.competency_name,
    });
  }

  return (
    <section className="card">
      <div className="item-form-header">
        {mode === 'edit' && (
          <button type="button" className="nav-btn" onClick={onNavigatePrev} disabled={!hasPrev} title="Item anterior">
            &#8592;
          </button>
        )}
        <h3 style={{ margin: 0 }}>{title}</h3>
        {mode === 'edit' && (
          <button type="button" className="nav-btn" onClick={onNavigateNext} disabled={!hasNext} title="Item siguiente">
            &#8594;
          </button>
        )}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <div className="grid grid-2">
          <label>
            Teacher ID
            <input
              type="number"
              min="1"
              value={form.teacher_id}
              onChange={(e) => onChange({ ...form, teacher_id: e.target.value })}
              required
              disabled={mode === 'edit'}
            />
          </label>
          <label>
            Respuesta correcta
            <select
              value={form.correct_answer}
              onChange={(e) => onChange({ ...form, correct_answer: e.target.value })}
            >
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
            </select>
          </label>
        </div>

        <label>
          Enunciado
          <RichTextEditor
            value={form.statement_doc}
            onChange={(value) => onChange({ ...form, statement_doc: value })}
            placeholder="Escribe el enunciado..."
            minHeight="180px"
          />
        </label>

        <div className="grid grid-2">
          <label>
            Opcion A
            <RichTextEditor
              value={form.optionA_doc}
              onChange={(value) => onChange({ ...form, optionA_doc: value })}
              placeholder="Contenido opcion A"
              minHeight="110px"
            />
          </label>
          <label>
            Opcion B
            <RichTextEditor
              value={form.optionB_doc}
              onChange={(value) => onChange({ ...form, optionB_doc: value })}
              placeholder="Contenido opcion B"
              minHeight="110px"
            />
          </label>
          <label>
            Opcion C
            <RichTextEditor
              value={form.optionC_doc}
              onChange={(value) => onChange({ ...form, optionC_doc: value })}
              placeholder="Contenido opcion C"
              minHeight="110px"
            />
          </label>
          <label>
            Opcion D
            <RichTextEditor
              value={form.optionD_doc}
              onChange={(value) => onChange({ ...form, optionD_doc: value })}
              placeholder="Contenido opcion D"
              minHeight="110px"
            />
          </label>
        </div>

        <div className="grid grid-2">
          <label>
            Area
            <input value={form.subject} onChange={(e) => onChange({ ...form, subject: e.target.value })} />
          </label>
          <label>
            Dificultad
            <input value={form.difficulty} onChange={(e) => onChange({ ...form, difficulty: e.target.value })} />
          </label>
        </div>

        <h4>Curricular (lite)</h4>
        <div className="grid grid-2">
          <label>
            Standard code
            <input
              list="standard-code-options"
              value={form.standard_code}
              onChange={(e) => handleStandardCodeChange(e.target.value)}
            />
          </label>
          <datalist id="standard-code-options">
            {standardOptions.map((row) => (
              <option key={row.id} value={row.code}>
                {row.name}
              </option>
            ))}
          </datalist>
          <label>
            Standard name
            <input
              value={form.standard_name}
              onChange={(e) => onChange({ ...form, standard_name: e.target.value })}
            />
          </label>
          <label>
            Competency code
            <input
              list="competency-code-options"
              value={form.competency_code}
              onChange={(e) => handleCompetencyCodeChange(e.target.value)}
            />
          </label>
          <datalist id="competency-code-options">
            {competencyOptions.map((row) => (
              <option key={row.id} value={row.code}>
                {row.name}
              </option>
            ))}
          </datalist>
          <label>
            Competency name
            <input
              value={form.competency_name}
              onChange={(e) => onChange({ ...form, competency_name: e.target.value })}
            />
          </label>
        </div>

        <div className="actions">
          <button type="submit" disabled={isSaving}>
            {isSaving ? 'Guardando...' : 'Guardar item'}
          </button>
          <button type="button" onClick={onReset}>
            Nuevo
          </button>
          {mode === 'edit' && (
            <button type="button" className="btn-danger" onClick={onDelete} disabled={isSaving}>
              Borrar item
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
