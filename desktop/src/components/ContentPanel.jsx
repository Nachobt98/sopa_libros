import { analyzeThematicContent } from "../model/contentAnalysis.js";

export function ContentPanel({
  contentState,
  inputPath,
  isVisible,
}) {
  const canLoad = contentState.canUseFiles && !contentState.isLoadingContent && inputPath.trim();
  const canSave = contentState.canUseFiles && !contentState.isSavingContent && inputPath.trim();
  const loadedLabel = contentState.loadedPath || "No content loaded";
  const analysis = analyzeThematicContent(contentState.content);

  return (
    <section id="content-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="content-heading">
      <div className="section-heading">
        <div>
          <h3 id="content-heading">Contenido</h3>
          <p>Edita el TXT tematico que usa la validacion y la generacion.</p>
        </div>
        <div className="content-actions">
          <button
            id="load-content"
            className="secondary-button"
            type="button"
            onClick={() => contentState.loadContent(inputPath)}
            disabled={!canLoad}
          >
            {contentState.isLoadingContent ? "Cargando..." : "Cargar TXT"}
          </button>
          <button
            id="save-content"
            className="primary-button"
            type="button"
            onClick={() => contentState.saveContent(inputPath)}
            disabled={!canSave}
          >
            {contentState.isSavingContent ? "Guardando..." : "Guardar TXT"}
          </button>
          <button className="secondary-button" type="button" onClick={contentState.insertTemplate}>
            Insertar plantilla
          </button>
          <button className="secondary-button" type="button" onClick={contentState.insertPuzzle}>
            Insertar puzzle
          </button>
        </div>
      </div>

      <div className="content-workbench">
        <div>
          <div className="content-status">
            <span>{contentState.isDirty ? "Contenido sin guardar" : "Contenido guardado"}</span>
            <code>{loadedLabel === "No content loaded" ? "Sin contenido cargado" : loadedLabel}</code>
          </div>

          <textarea
            id="content-editor"
            className="content-editor"
            value={contentState.content}
            onChange={(event) => contentState.setContent(event.target.value)}
            spellCheck="false"
          />
        </div>

        <aside className="content-inspector" aria-label="Resumen del contenido">
          <h4>Resumen</h4>
          <div className="content-metrics">
            <Metric label="Bloques" value={analysis.blockCount} />
            <Metric label="Puzzles" value={analysis.puzzleCount} />
            <Metric label="Palabras" value={analysis.wordCount} />
          </div>
          <h4>Bloques detectados</h4>
          {analysis.blocks.length ? (
            <ul>
              {analysis.blocks.map((block) => (
                <li key={block.slug}>{block.name}</li>
              ))}
            </ul>
          ) : (
            <p>No hay bloques detectados.</p>
          )}
          <h4>Validacion rapida</h4>
          {analysis.issues.length ? (
            <ul className="issue-list">
              {analysis.issues.map((issue) => (
                <li key={`${issue.line}-${issue.message}`}>Linea {issue.line}: {issue.message}</li>
              ))}
            </ul>
          ) : (
            <p>Sin incidencias basicas.</p>
          )}
        </aside>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
