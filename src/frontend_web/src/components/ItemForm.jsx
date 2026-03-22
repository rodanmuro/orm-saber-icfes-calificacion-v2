import { useEffect, useMemo, useState } from 'react';

import RichTextEditor from './RichTextEditor';
import {
  generateItemAIDraft,
  listCurriculumCompetencies,
  listCurriculumStandards,
} from '../api/itemsApi';
import { docToStorage, emptyDoc, storageToDoc, textToDoc } from '../utils/editorDoc';

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
  standard_name: '',
  _standard_id: null,
  competency_name: '',
  metadata: {},
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
    standard_name: item.curriculum?.standard_name || '',
    _standard_id: null,
    competency_name: item.curriculum?.competency_name || '',
    metadata: item.metadata || {},
  };
}

export function emptyForm() {
  return {
    ...EMPTY_FORM,
    statement_doc: emptyDoc(),
    optionA_doc: emptyDoc(),
    optionB_doc: emptyDoc(),
    optionC_doc: emptyDoc(),
    optionD_doc: emptyDoc(),
    metadata: {},
  };
}

export function formToPayload(form) {
  const curriculum =
    form.standard_name || form.competency_name
      ? {
          standard_name: form.standard_name || null,
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
    metadata:
      form.metadata && Object.keys(form.metadata).length > 0
        ? form.metadata
        : null,
  };
}

export default function ItemForm({
  form,
  onChange,
  onSubmit,
  onReset,
  onDelete,
  onNavigatePrev,
  onNavigateNext,
  hasPrev,
  hasNext,
  isSaving,
  mode,
}) {
  const title = useMemo(
    () => (mode === 'edit' ? `Editar item #${form.id}` : 'Nuevo item'),
    [mode, form.id]
  );
  const [standardOptions, setStandardOptions] = useState([]);
  const [competencyOptions, setCompetencyOptions] = useState([]);

  const [aiPrompt, setAiPrompt] = useState('');
  const [aiDraft, setAiDraft] = useState(null);
  const [aiUsage, setAiUsage] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  const [aiMessages, setAiMessages] = useState([]);

  useEffect(() => {
    let cancelled = false;
    listCurriculumStandards(form.standard_name)
      .then((rows) => {
        if (!cancelled) setStandardOptions(rows);
      })
      .catch(() => {
        if (!cancelled) setStandardOptions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [form.standard_name]);

  useEffect(() => {
    let cancelled = false;
    if (!form._standard_id && !form.standard_name) {
      setCompetencyOptions([]);
      return () => {
        cancelled = true;
      };
    }
    listCurriculumCompetencies({ standardId: form._standard_id, query: form.competency_name })
      .then((rows) => {
        if (!cancelled) setCompetencyOptions(rows);
      })
      .catch(() => {
        if (!cancelled) setCompetencyOptions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [form._standard_id, form.standard_name, form.competency_name]);

  function handleStandardChange(value) {
    const match = standardOptions.find((row) => row.name === value);
    onChange({
      ...form,
      standard_name: value,
      _standard_id: match?.id || null,
      competency_name: '',
    });
  }

  function handleCompetencyChange(value) {
    onChange({ ...form, competency_name: value });
  }

  function pushAiMessage(role, text) {
    setAiMessages((prev) => [
      ...prev,
      { id: `${Date.now()}-${Math.random()}`, role, text },
    ]);
  }

  async function handleGenerateWithAI() {
    const standardName = (form.standard_name || '').trim();
    const competencyName = (form.competency_name || '').trim();
    const userPrompt = aiPrompt.trim();

    setAiError('');
    setAiUsage(null);

    if (!standardName || !competencyName) {
      setAiError('Define Estandar y Competencia antes de generar con IA.');
      return;
    }
    if (!userPrompt) {
      setAiError('Escribe una instruccion para la IA.');
      return;
    }

    setAiLoading(true);
    pushAiMessage('user', userPrompt);

    try {
      const response = await generateItemAIDraft({
        user_prompt: userPrompt,
        standard_name: standardName,
        competency_name: competencyName,
        subject: form.subject || null,
        difficulty: form.difficulty || null,
      });
      setAiDraft(response);
      setAiUsage(response.usage || null);
      onChange({
        ...form,
        statement_doc: textToDoc(response.statement),
        optionA_doc: textToDoc(response.options?.A || ""),
        optionB_doc: textToDoc(response.options?.B || ""),
        optionC_doc: textToDoc(response.options?.C || ""),
        optionD_doc: textToDoc(response.options?.D || ""),
        correct_answer: response.correct_answer || form.correct_answer,
        metadata: {
          ...(form.metadata || {}),
          ...(response.metadata || {}),
        },
      });
      pushAiMessage(
        'assistant',
        'Borrador generado y aplicado al formulario. Correcta sugerida: ' +
          response.correct_answer +
          '. Revisa y luego guarda manualmente.'
      );
    } catch (err) {
      const message = err?.message || 'Error generando borrador con IA';
      setAiError(message);
      pushAiMessage('system', `Error: ${message}`);
    } finally {
      setAiLoading(false);
    }
  }

  function handleApplyAIDraft() {
    if (!aiDraft) return;

    onChange({
      ...form,
      statement_doc: textToDoc(aiDraft.statement),
      optionA_doc: textToDoc(aiDraft.options?.A || ''),
      optionB_doc: textToDoc(aiDraft.options?.B || ''),
      optionC_doc: textToDoc(aiDraft.options?.C || ''),
      optionD_doc: textToDoc(aiDraft.options?.D || ''),
      correct_answer: aiDraft.correct_answer || form.correct_answer,
      metadata: {
        ...(form.metadata || {}),
        ...(aiDraft.metadata || {}),
      },
    });

    pushAiMessage('system', 'Borrador IA aplicado al formulario. Revisa y guarda manualmente.');
  }

  return (
    <section className="card">
      <div className="item-form-header">
        <button
          type="button"
          className="nav-btn"
          onClick={onNavigatePrev}
          disabled={!hasPrev}
          title="Item anterior"
        >
          &#8592;
        </button>
        <h3 style={{ margin: 0 }}>{title}</h3>
        <button
          type="button"
          className="nav-btn"
          onClick={onNavigateNext}
          disabled={!hasNext}
          title="Item siguiente"
        >
          &#8594;
        </button>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >


        <h4>Asistente IA (borrador)</h4>
        <div className="ai-panel">
          <label>
            Instruccion para IA
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Ej: Crea una pregunta de porcentajes para grado 7, con distractores comunes."
            />
          </label>

          <div className="actions">
            <button type="button" onClick={handleGenerateWithAI} disabled={aiLoading}>
              {aiLoading ? 'Generando borrador...' : 'Generar borrador IA'}
            </button>
            <button type="button" onClick={handleApplyAIDraft} disabled={!aiDraft || aiLoading}>
              Aplicar borrador IA
            </button>
          </div>

          {aiError ? <p className="alert error">{aiError}</p> : null}

          {aiUsage ? (
            <div className="ai-usage">
              <p><strong>Tokens entrada:</strong> {aiUsage.input_tokens} (cached: {aiUsage.cached_input_tokens})</p>
              <p><strong>Tokens salida:</strong> {aiUsage.output_tokens}</p>
              <p><strong>Total tokens:</strong> {aiUsage.total_tokens}</p>
              <p><strong>Costo entrada USD:</strong> {Number(aiUsage.input_cost_usd || 0).toFixed(8)}</p>
              <p><strong>Costo cached USD:</strong> {Number(aiUsage.cached_input_cost_usd || 0).toFixed(8)}</p>
              <p><strong>Costo salida USD:</strong> {Number(aiUsage.output_cost_usd || 0).toFixed(8)}</p>
              <p><strong>Costo total USD:</strong> {Number(aiUsage.total_cost_usd || 0).toFixed(8)}</p>
            </div>
          ) : null}

          <div className="ai-chat-log">
            {aiMessages.length === 0 ? (
              <p className="ai-chat-empty">
                Sin mensajes aun. La IA requiere Estandar y Competencia para generar.
              </p>
            ) : (
              aiMessages.map((msg) => (
                <div key={msg.id} className={`ai-chat-msg ${msg.role}`}>
                  <strong>{msg.role === 'user' ? 'Tu' : msg.role === 'assistant' ? 'IA' : 'Sistema'}:</strong>{' '}
                  {msg.text}
                </div>
              ))
            )}
          </div>
        </div>
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
            <input
              value={form.subject}
              onChange={(e) => onChange({ ...form, subject: e.target.value })}
            />
          </label>
          <label>
            Dificultad
            <input
              value={form.difficulty}
              onChange={(e) => onChange({ ...form, difficulty: e.target.value })}
            />
          </label>
        </div>

        <h4>Curricular</h4>
        <div className="grid grid-2">
          <label>
            Estandar
            <input
              list="standard-name-options"
              value={form.standard_name}
              onChange={(e) => handleStandardChange(e.target.value)}
              placeholder="Nombre del estandar..."
            />
            <datalist id="standard-name-options">
              {standardOptions.map((row) => (
                <option key={row.id} value={row.name} />
              ))}
            </datalist>
          </label>
          <label>
            Competencia
            <input
              list="competency-name-options"
              value={form.competency_name}
              onChange={(e) => handleCompetencyChange(e.target.value)}
              placeholder="Nombre de la competencia..."
              disabled={!form.standard_name}
            />
            <datalist id="competency-name-options">
              {competencyOptions.map((row) => (
                <option key={row.id} value={row.name} />
              ))}
            </datalist>
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
