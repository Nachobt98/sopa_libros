export const starterContentTemplate = `[Block]
name: Ancient Egypt
[/Block]

[Puzzle]
title: Pharaohs and Queens
fact: Pharaohs ruled ancient Egypt and built monuments that still shape history.
words:
NILE
PYRAMID
PHARAOH
SCARAB
TEMPLE
SCRIBE
[/Puzzle]
`;

export function slugifyName(value) {
  return String(value || "default")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "") || "default";
}

export function analyzeThematicContent(content) {
  const lines = String(content || "").split(/\r?\n/);
  const issues = [];
  const blocks = [];
  let puzzleCount = 0;
  let wordCount = 0;
  let currentBlock = null;
  let inPuzzle = false;
  let currentPuzzle = null;
  let readingWords = false;

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();
    if (!line) {
      return;
    }

    if (line === "[Block]") {
      currentBlock = { line: index + 1, name: "" };
      return;
    }
    if (line === "[/Block]") {
      if (currentBlock?.name) {
        blocks.push({ name: currentBlock.name, slug: slugifyName(currentBlock.name) });
      } else {
        issues.push({ line: currentBlock?.line || index + 1, message: "Bloque sin name:." });
      }
      currentBlock = null;
      return;
    }
    if (currentBlock && line.toLowerCase().startsWith("name:")) {
      currentBlock.name = line.slice(5).trim();
      return;
    }

    if (line === "[Puzzle]") {
      inPuzzle = true;
      readingWords = false;
      currentPuzzle = { line: index + 1, title: "", fact: "", words: [] };
      return;
    }
    if (line === "[/Puzzle]") {
      if (!currentPuzzle?.title) {
        issues.push({ line: currentPuzzle?.line || index + 1, message: "Puzzle sin title:." });
      }
      if (!currentPuzzle?.fact) {
        issues.push({ line: currentPuzzle?.line || index + 1, message: "Puzzle sin fact:." });
      }
      if (!currentPuzzle?.words.length) {
        issues.push({ line: currentPuzzle?.line || index + 1, message: "Puzzle sin palabras." });
      }
      puzzleCount += 1;
      wordCount += currentPuzzle?.words.length || 0;
      inPuzzle = false;
      readingWords = false;
      currentPuzzle = null;
      return;
    }

    if (!inPuzzle || !currentPuzzle) {
      return;
    }
    if (line.toLowerCase().startsWith("title:")) {
      currentPuzzle.title = line.slice(6).trim();
      readingWords = false;
      return;
    }
    if (line.toLowerCase().startsWith("fact:")) {
      currentPuzzle.fact = line.slice(5).trim();
      readingWords = false;
      return;
    }
    if (line.toLowerCase() === "words:") {
      readingWords = true;
      return;
    }
    if (readingWords) {
      currentPuzzle.words.push(line);
    }
  });

  if (currentBlock) {
    issues.push({ line: currentBlock.line, message: "Bloque sin cierre [/Block]." });
  }
  if (inPuzzle && currentPuzzle) {
    issues.push({ line: currentPuzzle.line, message: "Puzzle sin cierre [/Puzzle]." });
  }

  return {
    blockCount: blocks.length,
    blocks,
    issueCount: issues.length,
    issues,
    puzzleCount,
    wordCount,
  };
}
