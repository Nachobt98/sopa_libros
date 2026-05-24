import { useState } from "react";

const formatHelp = {
  "trade-6x9": "Formato compacto para libros de lectura y colecciones medianas.",
  "activity-8.5x11": "Formato grande para actividad, mejor para puzzles amplios.",
  "large-print-8x10": "Pensado para letra grande y mejor legibilidad.",
  "square-8.5": "Formato cuadrado para previews y estilos visuales especiales.",
};

export function ProjectForm({ project, setProject }) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  function updateField(field, value) {
    setProject((current) => ({ ...current, [field]: value }));
  }

  return (
    <form id="project-form" className="project-form">
      <section className="form-section">
        <h4>Libro</h4>
        <div className="editor-grid">
          <label>
            <span>Titulo del libro</span>
            <input
              id="book-title"
              name="bookTitle"
              type="text"
              autoComplete="off"
              value={project.book_title}
              onChange={(event) => updateField("book_title", event.target.value)}
            />
          </label>

          <label>
            <span>TXT tematico</span>
            <input
              id="input-path"
              name="inputPath"
              type="text"
              autoComplete="off"
              value={project.input_path}
              onChange={(event) => updateField("input_path", event.target.value)}
            />
          </label>
        </div>
      </section>

      <section className="form-section">
        <h4>Generacion</h4>
        <div className="editor-grid">
          <fieldset className="segmented-field">
            <legend>Dificultad</legend>
            <div className="segmented" role="radiogroup" aria-label="Difficulty">
              {["easy", "medium", "hard"].map((difficulty) => (
                <button
                  key={difficulty}
                  type="button"
                  className={project.difficulty === difficulty ? "is-selected" : ""}
                  onClick={() => updateField("difficulty", difficulty)}
                >
                  {difficulty === "easy" ? "Facil" : difficulty === "medium" ? "Media" : "Dificil"}
                </button>
              ))}
            </div>
          </fieldset>

          <label>
            <span>Tamano de grid</span>
            <input
              id="grid-size"
              name="gridSize"
              type="number"
              min="6"
              max="30"
              step="1"
              value={project.grid_size}
              onChange={(event) => updateField("grid_size", event.target.value)}
            />
          </label>
        </div>
      </section>

      <section className="form-section">
        <h4>Diseno y salida</h4>
        <div className="editor-grid">
          <label>
            <span>Tema visual</span>
            <select
              id="theme-name"
              name="themeName"
              value={project.theme_name}
              onChange={(event) => updateField("theme_name", event.target.value)}
            >
              <option value="current-default">Actual por defecto</option>
              <option value="premium-neutral">Premium neutral</option>
              <option value="bold-modern">Bold modern</option>
              <option value="kids">Kids</option>
            </select>
          </label>

          <label>
            <span>Formato</span>
            <select
              id="format-name"
              name="formatName"
              value={project.format_name}
              onChange={(event) => updateField("format_name", event.target.value)}
            >
              <option value="trade-6x9">Trade 6 x 9</option>
              <option value="activity-8.5x11">Activity 8.5 x 11</option>
              <option value="large-print-8x10">Large print 8 x 10</option>
              <option value="square-8.5">Square 8.5</option>
            </select>
            <small>{formatHelp[project.format_name]}</small>
          </label>
        </div>
      </section>

      <section className="form-section">
        <button className="link-button" type="button" onClick={() => setShowAdvanced((value) => !value)}>
          {showAdvanced ? "Ocultar avanzado" : "Mostrar avanzado"}
        </button>
        {showAdvanced ? (
          <div className="editor-grid advanced-grid">
            <label>
              <span>Manifest de tema</span>
              <input
                id="theme-manifest"
                name="themeManifestPath"
                type="text"
                autoComplete="off"
                value={project.theme_manifest_path || ""}
                onChange={(event) => updateField("theme_manifest_path", event.target.value)}
              />
            </label>

            <label>
              <span>Carpeta de salida</span>
              <input
                id="output-dir"
                name="outputDir"
                type="text"
                autoComplete="off"
                value={project.output_dir || ""}
                onChange={(event) => updateField("output_dir", event.target.value)}
              />
            </label>

            <label>
              <span>Seed</span>
              <input
                id="seed"
                name="seed"
                type="number"
                step="1"
                value={project.seed ?? ""}
                onChange={(event) => updateField("seed", event.target.value)}
              />
            </label>

            <label>
              <span>Limite de puzzles</span>
              <input
                id="limit"
                name="limit"
                type="number"
                min="1"
                step="1"
                value={project.limit ?? ""}
                onChange={(event) => updateField("limit", event.target.value)}
              />
            </label>
          </div>
        ) : null}
      </section>

      <label className="toggle-row">
        <input
          id="preview"
          name="preview"
          type="checkbox"
          checked={project.preview}
          onChange={(event) => updateField("preview", event.target.checked)}
        />
        <span>Modo preview</span>
      </label>
    </form>
  );
}
