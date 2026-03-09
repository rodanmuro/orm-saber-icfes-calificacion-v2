export default function FiltersBar({ filters, onChange, onClear }) {
  return (
    <section className="card">
      <h3>Filtros</h3>
      <div className="grid grid-3">
        <label>
          Area
          <input
            value={filters.subject}
            onChange={(e) => onChange({ ...filters, subject: e.target.value })}
            placeholder="Ej: matematicas"
          />
        </label>
        <label>
          Dificultad
          <input
            value={filters.difficulty}
            onChange={(e) => onChange({ ...filters, difficulty: e.target.value })}
            placeholder="Ej: media"
          />
        </label>
        <label>
          Etiqueta curricular
          <input
            value={filters.curricularTag}
            onChange={(e) => onChange({ ...filters, curricularTag: e.target.value })}
            placeholder="standard/competency"
          />
        </label>
      </div>
      <button type="button" onClick={onClear}>Limpiar filtros</button>
    </section>
  );
}
