import { useMemo, useState } from 'react';

function emptyExamForm(defaultTeacherId) {
  return {
    teacher_id: defaultTeacherId || 1,
    exam_code: '',
    title: '',
    description: '',
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
  onPublishVersion,
  loading,
}) {
  const [form, setForm] = useState(emptyExamForm(exams[0]?.teacher_id || 1));

  const itemsNotAdded = useMemo(() => {
    if (!selectedExam) return [];
    const existing = new Set(selectedExam.items.map((row) => row.item_id));
    return items.filter((item) => !existing.has(item.id));
  }, [items, selectedExam]);

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
          Exam code
          <input
            value={form.exam_code}
            onChange={(e) => setForm({ ...form, exam_code: e.target.value })}
            placeholder="Ej: MAT-001"
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
        <button type="button" onClick={() => onRefreshExams(form.teacher_id)}>
          Recargar examenes
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
                <td>
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
            Examen seleccionado: #{selectedExam.id} - {selectedExam.exam_code}
          </h4>
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
            <div>
              <h5>Items disponibles</h5>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Enunciado</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {itemsNotAdded.map((item) => (
                      <tr key={item.id}>
                        <td>{item.id}</td>
                        <td>{item.statement}</td>
                        <td>
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

            <div>
              <h5>Items asociados (orden inicial)</h5>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Orden</th>
                      <th>Item ID</th>
                      <th>Enunciado</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedExam.items.map((row) => (
                      <tr key={`${row.exam_id}-${row.item_id}`}>
                        <td>{row.order_position}</td>
                        <td>{row.item_id}</td>
                        <td>{row.item_statement}</td>
                        <td>
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
    </section>
  );
}
