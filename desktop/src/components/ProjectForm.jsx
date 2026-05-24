export function ProjectForm({ project, setProject }) {
  function updateField(field, value) {
    setProject((current) => ({ ...current, [field]: value }));
  }

  return (
    <form id="project-form" className="editor-grid">
      <label>
        <span>Book title</span>
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
        <span>Thematic TXT input</span>
        <input
          id="input-path"
          name="inputPath"
          type="text"
          autoComplete="off"
          value={project.input_path}
          onChange={(event) => updateField("input_path", event.target.value)}
        />
      </label>

      <label>
        <span>Theme manifest</span>
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
        <span>Output directory</span>
        <input
          id="output-dir"
          name="outputDir"
          type="text"
          autoComplete="off"
          value={project.output_dir || ""}
          onChange={(event) => updateField("output_dir", event.target.value)}
        />
      </label>

      <fieldset className="segmented-field">
        <legend>Difficulty</legend>
        <div className="segmented" role="radiogroup" aria-label="Difficulty">
          {["easy", "medium", "hard"].map((difficulty) => (
            <button
              key={difficulty}
              type="button"
              className={project.difficulty === difficulty ? "is-selected" : ""}
              onClick={() => updateField("difficulty", difficulty)}
            >
              {difficulty[0].toUpperCase() + difficulty.slice(1)}
            </button>
          ))}
        </div>
      </fieldset>

      <label>
        <span>Grid size</span>
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
        <span>Puzzle limit</span>
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

      <label>
        <span>Theme</span>
        <select
          id="theme-name"
          name="themeName"
          value={project.theme_name}
          onChange={(event) => updateField("theme_name", event.target.value)}
        >
          <option value="current-default">Current default</option>
          <option value="premium-neutral">Premium neutral</option>
          <option value="bold-modern">Bold modern</option>
          <option value="kids">Kids</option>
        </select>
      </label>

      <label>
        <span>Format</span>
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
      </label>

      <label className="toggle-row">
        <input
          id="preview"
          name="preview"
          type="checkbox"
          checked={project.preview}
          onChange={(event) => updateField("preview", event.target.checked)}
        />
        <span>Preview mode</span>
      </label>
    </form>
  );
}
