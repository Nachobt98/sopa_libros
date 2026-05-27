import { useMemo } from "react";
import { parseThematicContent } from "../model/contentAnalysis.js";

function buildPreviewLetters(words, size) {
  const source = (words.join("") || "PUZZLEFORGESTUDIO").replace(/[^A-Za-z]/g, "").toUpperCase();
  const letters = [];
  for (let index = 0; index < size * size; index += 1) {
    letters.push(source[index % source.length] || "X");
  }
  return letters;
}

function GridPreview({ size, words }) {
  const letters = useMemo(() => buildPreviewLetters(words, size), [size, words]);
  return (
    <div id="preview-grid" className="preview-grid" style={{ gridTemplateColumns: `repeat(${size}, 1fr)` }} aria-hidden="true">
      {letters.map((letter, index) => (
        <span key={`${letter}-${index}`}>{letter}</span>
      ))}
    </div>
  );
}

function WordsPreview({ words }) {
  return (
    <div id="preview-words" className="preview-words">
      {words.slice(0, 10).map((word) => (
        <span key={word}>{word}</span>
      ))}
    </div>
  );
}

export function PreviewRail({ content, project, toast }) {
  const model = useMemo(() => parseThematicContent(content), [content]);
  const puzzle = model.puzzles[0] || {
    blockName: "Preview",
    fact: "Carga o crea contenido para ver una preview mas representativa.",
    title: project.book_title,
    words: ["PUZZLE", "FORGE", "KDP", "LIBRO"],
  };
  const previewSize = Math.max(8, Math.min(12, Number(project.grid_size || 10)));
  const words = puzzle.words.length ? puzzle.words : ["PUZZLE", "FORGE"];

  return (
    <aside className="preview-rail" aria-label="Book preview">
      <div className="book-preview">
        <div className="preview-tabs" aria-label="Preview modes">
          <span className="is-active">Puzzle</span>
          <span>Cover</span>
          <span>PDF</span>
        </div>
        <div className="page-preview">
          <div className="page-label">{puzzle.blockName || "Puzzle 01"}</div>
          <div id="preview-title" className="preview-title">
            {puzzle.title || project.book_title}
          </div>
          <GridPreview size={previewSize} words={words} />
          <WordsPreview words={words} />
          {puzzle.fact ? <p className="preview-fact">{puzzle.fact}</p> : null}
        </div>
        <div className="preview-meta">
          <div>
            <span>Formato</span>
            <strong>{project.format_name}</strong>
          </div>
          <div>
            <span>Grid</span>
            <strong>{project.grid_size} x {project.grid_size}</strong>
          </div>
          <div>
            <span>Puzzles</span>
            <strong>{model.puzzles.length || 1}</strong>
          </div>
        </div>
      </div>
      <div id="toast" className="toast" role="status" aria-live="polite">
        {toast}
      </div>
    </aside>
  );
}
