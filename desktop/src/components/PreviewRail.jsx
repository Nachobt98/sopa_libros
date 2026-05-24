import { sampleLetters, sampleWords } from "../model/project.js";

function GridPreview() {
  return (
    <div id="preview-grid" className="preview-grid" aria-hidden="true">
      {Array.from({ length: 100 }, (_, index) => (
        <span key={index}>{sampleLetters[index % sampleLetters.length]}</span>
      ))}
    </div>
  );
}

function WordsPreview() {
  return (
    <div id="preview-words" className="preview-words">
      {sampleWords.map((word) => (
        <span key={word}>{word}</span>
      ))}
    </div>
  );
}

export function PreviewRail({ title, toast }) {
  return (
    <aside className="preview-rail" aria-label="Book preview">
      <div className="book-preview">
        <div className="page-preview">
          <div className="page-label">Puzzle 01</div>
          <div id="preview-title" className="preview-title">
            {title}
          </div>
          <GridPreview />
          <WordsPreview />
        </div>
      </div>
      <div id="toast" className="toast" role="status" aria-live="polite">
        {toast}
      </div>
    </aside>
  );
}
