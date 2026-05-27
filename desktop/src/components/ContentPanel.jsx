import { useMemo, useState } from "react";
import {
  analyzeThematicContent,
  createEmptyContentModel,
  parseThematicContent,
  serializeThematicContent,
  slugifyName,
} from "../model/contentAnalysis.js";

export function ContentPanel({ contentState, inputPath, isVisible }) {
  const [selectedPuzzleIndex, setSelectedPuzzleIndex] = useState(0);
  const [showRaw, setShowRaw] = useState(false);
  const canLoad = contentState.canUseFiles && !contentState.isLoadingContent && inputPath.trim();
  const canSave = contentState.canUseFiles && !contentState.isSavingContent && inputPath.trim();
  const loadedLabel = contentState.loadedPath || "No content loaded";
  const model = useMemo(
    () => (contentState.content.trim() ? parseThematicContent(contentState.content) : createEmptyContentModel()),
    [contentState.content]
  );
  const analysis = analyzeThematicContent(contentState.content || serializeThematicContent(model));
  const selectedPuzzle = model.puzzles[selectedPuzzleIndex] || model.puzzles[0] || null;

  function commitModel(nextModel) {
    contentState.setContent(serializeThematicContent(nextModel));
  }

  function updatePuzzle(field, value) {
    const nextPuzzles = model.puzzles.map((puzzle, index) =>
      index === selectedPuzzleIndex ? { ...puzzle, [field]: value } : puzzle
    );
    commitModel({ ...model, puzzles: nextPuzzles });
  }

  function updateSelectedWords(value) {
    updatePuzzle(
      "words",
      value
        .split(/\r?\n/)
        .map((word) => word.trim())
        .filter(Boolean)
    );
  }

  function addBlock() {
    const name = `Bloque ${model.blocks.length + 1}`;
    commitModel({
      ...model,
      blocks: [...model.blocks, { name, slug: slugifyName(name) }],
    });
  }

  function addPuzzle() {
    const blockName = model.blocks[0]?.name || "Nuevo bloque";
    const nextPuzzle = {
      blockName,
      fact: "Escribe aqui un dato breve para este puzzle.",
      title: `Puzzle ${model.puzzles.length + 1}`,
      words: ["PALABRA", "SEGUNDA", "TERCERA"],
    };
    commitModel({ ...model, puzzles: [...model.puzzles, nextPuzzle] });
    setSelectedPuzzleIndex(model.puzzles.length);
  }

  function removeSelectedPuzzle() {
    if (model.puzzles.length <= 1) {
      return;
    }
    const nextPuzzles = model.puzzles.filter((_, index) => index !== selectedPuzzleIndex);
    commitModel({ ...model, puzzles: nextPuzzles });
    setSelectedPuzzleIndex(Math.max(0, selectedPuzzleIndex - 1));
  }

  function updateBlockName(index, name) {
    const previousName = model.blocks[index]?.name;
    const nextBlocks = model.blocks.map((block, blockIndex) =>
      blockIndex === index ? { name, slug: slugifyName(name) } : block
    );
    const nextPuzzles = model.puzzles.map((puzzle) =>
      puzzle.blockName === previousName ? { ...puzzle, blockName: name } : puzzle
    );
    commitModel({ ...model, blocks: nextBlocks, puzzles: nextPuzzles });
  }

  return (
    <section id="content-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="content-heading">
      <div className="section-heading">
        <div>
          <h3 id="content-heading">Contenido</h3>
          <p>Edita bloques, puzzles, facts y palabras sin tocar el TXT manualmente.</p>
        </div>
        <div className="content-actions">
          <button id="load-content" className="secondary-button" type="button" onClick={() => contentState.loadContent(inputPath)} disabled={!canLoad}>
            {contentState.isLoadingContent ? "Cargando..." : "Cargar TXT"}
          </button>
          <button id="save-content" className="primary-button" type="button" onClick={() => contentState.saveContent(inputPath)} disabled={!canSave}>
            {contentState.isSavingContent ? "Guardando..." : "Guardar TXT"}
          </button>
          <button className="secondary-button" type="button" onClick={() => commitModel(createEmptyContentModel())}>
            Plantilla visual
          </button>
          <button className="secondary-button" type="button" onClick={() => setShowRaw((value) => !value)}>
            {showRaw ? "Ocultar TXT" : "Ver TXT"}
          </button>
        </div>
      </div>

      <div className="content-status">
        <span>{contentState.isDirty ? "Contenido sin guardar" : "Contenido guardado"}</span>
        <code>{loadedLabel === "No content loaded" ? "Sin contenido cargado" : loadedLabel}</code>
      </div>

      <div className="visual-content-layout">
        <aside className="puzzle-list-panel">
          <div className="panel-title-row">
            <h4>Puzzles</h4>
            <button type="button" onClick={addPuzzle}>+</button>
          </div>
          <div className="puzzle-list">
            {model.puzzles.map((puzzle, index) => (
              <button
                key={`${puzzle.title}-${index}`}
                className={index === selectedPuzzleIndex ? "is-selected" : ""}
                type="button"
                onClick={() => setSelectedPuzzleIndex(index)}
              >
                <strong>{puzzle.title || `Puzzle ${index + 1}`}</strong>
                <span>{puzzle.blockName || "Sin bloque"} · {puzzle.words.length} palabras</span>
              </button>
            ))}
          </div>
        </aside>

        <div className="puzzle-editor-panel">
          {selectedPuzzle ? (
            <>
              <div className="panel-title-row">
                <h4>Editor visual</h4>
                <button className="link-button" type="button" onClick={removeSelectedPuzzle} disabled={model.puzzles.length <= 1}>
                  Eliminar puzzle
                </button>
              </div>

              <div className="editor-grid">
                <label>
                  <span>Titulo del puzzle</span>
                  <input value={selectedPuzzle.title} onChange={(event) => updatePuzzle("title", event.target.value)} />
                </label>

                <label>
                  <span>Bloque</span>
                  <select value={selectedPuzzle.blockName || ""} onChange={(event) => updatePuzzle("blockName", event.target.value)}>
                    {model.blocks.map((block) => (
                      <option key={block.slug} value={block.name}>{block.name}</option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="wide-field">
                <span>Fact / texto de apoyo</span>
                <textarea
                  className="fact-editor"
                  value={selectedPuzzle.fact}
                  onChange={(event) => updatePuzzle("fact", event.target.value)}
                />
              </label>

              <label className="wide-field">
                <span>Palabras, una por linea</span>
                <textarea
                  className="words-editor"
                  value={selectedPuzzle.words.join("\n")}
                  onChange={(event) => updateSelectedWords(event.target.value)}
                />
              </label>
            </>
          ) : null}
        </div>

        <aside className="content-inspector" aria-label="Resumen del contenido">
          <div className="panel-title-row">
            <h4>Bloques</h4>
            <button type="button" onClick={addBlock}>+</button>
          </div>
          <div className="block-editor-list">
            {model.blocks.map((block, index) => (
              <label key={`${block.slug}-${index}`}>
                <span>Bloque {index + 1}</span>
                <input value={block.name} onChange={(event) => updateBlockName(index, event.target.value)} />
              </label>
            ))}
          </div>

          <h4>Resumen</h4>
          <div className="content-metrics">
            <Metric label="Bloques" value={analysis.blockCount} />
            <Metric label="Puzzles" value={analysis.puzzleCount} />
            <Metric label="Palabras" value={analysis.wordCount} />
          </div>
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

      {showRaw ? (
        <textarea
          id="content-editor"
          className="content-editor is-raw"
          value={contentState.content}
          onChange={(event) => contentState.setContent(event.target.value)}
          spellCheck="false"
        />
      ) : null}
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
