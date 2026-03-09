import { useMemo } from 'react';

const EMPTY_FORM = {
  id: null,
  teacher_id: 1,
  statement: '',
  optionA: '',
  optionB: '',
  optionC: '',
  optionD: '',
  correct_answer: 'A',
  subject: '',
  difficulty: '',
  standard_code: '',
  standard_name: '',
  competency_code: '',
  competency_name: '',
};

export function itemToForm(item) {
  if (!item) return EMPTY_FORM;
  return {
    id: item.id,
    teacher_id: item.teacher_id,
    statement: item.statement || '',
    optionA: item.options?.A || '',
    optionB: item.options?.B || '',
    optionC: item.options?.C || '',
    optionD: item.options?.D || '',
    correct_answer: item.correct_answer || 'A',
    subject: item.subject || '',
    difficulty: item.difficulty || '',
    standard_code: item.curriculum?.standard_code || '',
    standard_name: item.curriculum?.standard_name || '',
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
          standard_code: form.standard_code || null,
          standard_name: form.standard_name || null,
          competency_code: form.competency_code || null,
          competency_name: form.competency_name || null,
        }
      : null;

  return {
    teacher_id: Number(form.teacher_id),
    statement: form.statement,
    options: {
      A: form.optionA,
      B: form.optionB,
      C: form.optionC,
      D: form.optionD,
    },
    correct_answer: form.correct_answer,
    subject: form.subject || null,
    difficulty: form.difficulty || null,
    curriculum,
  };
}

export default function ItemForm({ form, onChange, onSubmit, onReset, isSaving, mode }) {
  const title = useMemo(() => (mode === 'edit' ? `Editar item #${form.id}` : 'Crear item'), [mode, form.id]);

  return (
    <section className="card">
      <h3>{title}</h3>
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
          <textarea
            value={form.statement}
            onChange={(e) => onChange({ ...form, statement: e.target.value })}
            required
          />
        </label>

        <div className="grid grid-2">
          <label>
            Opcion A
            <input value={form.optionA} onChange={(e) => onChange({ ...form, optionA: e.target.value })} required />
          </label>
          <label>
            Opcion B
            <input value={form.optionB} onChange={(e) => onChange({ ...form, optionB: e.target.value })} required />
          </label>
          <label>
            Opcion C
            <input value={form.optionC} onChange={(e) => onChange({ ...form, optionC: e.target.value })} required />
          </label>
          <label>
            Opcion D
            <input value={form.optionD} onChange={(e) => onChange({ ...form, optionD: e.target.value })} required />
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
              value={form.standard_code}
              onChange={(e) => onChange({ ...form, standard_code: e.target.value })}
            />
          </label>
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
              value={form.competency_code}
              onChange={(e) => onChange({ ...form, competency_code: e.target.value })}
            />
          </label>
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
            {isSaving ? 'Guardando...' : mode === 'edit' ? 'Actualizar item' : 'Crear item'}
          </button>
          <button type="button" onClick={onReset}>
            Nuevo
          </button>
        </div>
      </form>
    </section>
  );
}
