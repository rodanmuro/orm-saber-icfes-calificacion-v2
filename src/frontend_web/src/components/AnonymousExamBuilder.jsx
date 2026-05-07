import { useMemo, useState } from 'react';

function emptyForm() {
  return {
    teacher_id: 1,
    exam_code: '',
    title: '',
    question_count: 10,
    source_pdf_path: '',
    is_active: true,
  };
}

function buildInitialAnswers(questionCount) {
  const rows = {};
  for (let i = 1; i <= questionCount; i += 1) rows[String(i)] = 'A';
  return rows;
}

export default function AnonymousExamBuilder({
  exams,
  loading,
  onRefresh,
  onCreate,
}) {
  const [form, setForm] = useState(emptyForm());
  const [answers, setAnswers] = useState(buildInitialAnswers(10));

  const normalizedCount = useMemo(
    () => Math.max(1, Math.min(200, Number(form.question_count) || 1)),
    [form.question_count],
  );

  function syncAnswers(nextCount) {
    const next = {};
    for (let i = 1; i <= nextCount; i += 1) {
      next[String(i)] = answers[String(i)] || 'A';
    }
    setAnswers(next);
  }

  function handleQuestionCountChange(raw) {
    const nextCount = Math.max(1, Math.min(200, Number(raw) || 1));
    setForm((prev) => ({ ...prev, question_count: nextCount }));
    syncAnswers(nextCount);
  }

  async function handleCreate() {
    const payload = {
      teacher_id: Number(form.teacher_id) || 1,
      exam_code: form.exam_code.trim() || null,
      title: form.title.trim(),
      question_count: normalizedCount,
      answer_key: answers,
      source_pdf_path: form.source_pdf_path.trim() || null,
      is_active: Boolean(form.is_active),
    };
    await onCreate(payload);
    await onRefresh(payload.teacher_id);
    setForm((prev) => ({ ...emptyForm(), teacher_id: payload.teacher_id }));
    setAnswers(buildInitialAnswers(10));
  }

  return (
    <section className="card">
      <h3>Examen anónimo</h3>
      <p className="helper-text">
        Crea un examen solo con clave de respuestas (sin items del banco).
      </p>
      <div className="grid grid-3">
        <label>
          Teacher ID
          <input
            type="number"
            min="1"
            value={form.teacher_id}
            onChange={(e) => setForm((prev) => ({ ...prev, teacher_id: Number(e.target.value) }))}
          />
        </label>
        <label>
          Código examen (opcional)
          <input
            value={form.exam_code}
            onChange={(e) => setForm((prev) => ({ ...prev, exam_code: e.target.value }))}
            placeholder="Ej: 7"
          />
        </label>
        <label>
          Número de preguntas
          <input
            type="number"
            min="1"
            max="200"
            value={form.question_count}
            onChange={(e) => handleQuestionCountChange(e.target.value)}
          />
        </label>
        <label>
          Título
          <input
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
            placeholder="Ej: Simulacro externo 11A"
          />
        </label>
        <label>
          Ruta PDF (opcional)
          <input
            value={form.source_pdf_path}
            onChange={(e) => setForm((prev) => ({ ...prev, source_pdf_path: e.target.value }))}
            placeholder="/ruta/al/cuadernillo.pdf"
          />
        </label>
      </div>

      <h4>Clave de respuestas</h4>
      <div className="table-wrap" style={{ maxHeight: 260 }}>
        <table>
          <thead>
            <tr>
              <th>Pregunta</th>
              <th>Correcta</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: normalizedCount }, (_, i) => i + 1).map((qn) => (
              <tr key={qn}>
                <td>{qn}</td>
                <td>
                  <select
                    value={answers[String(qn)] || 'A'}
                    onChange={(e) =>
                      setAnswers((prev) => ({ ...prev, [String(qn)]: e.target.value }))
                    }
                  >
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="actions">
        <button type="button" onClick={handleCreate}>
          Crear examen anónimo
        </button>
        <button type="button" onClick={() => onRefresh(Number(form.teacher_id) || 1)}>
          Recargar
        </button>
      </div>

      <h4>Exámenes anónimos</h4>
      {loading ? <p>Cargando...</p> : null}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Teacher</th>
              <th>Code</th>
              <th>Título</th>
              <th>Preguntas</th>
              <th>Activo</th>
            </tr>
          </thead>
          <tbody>
            {exams.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.teacher_id}</td>
                <td>{row.exam_code}</td>
                <td>{row.title}</td>
                <td>{row.question_count}</td>
                <td>{row.is_active ? 'Si' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
