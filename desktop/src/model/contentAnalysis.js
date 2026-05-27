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
  const model = parseThematicContent(content);
  return {
    blockCount: model.blocks.length,
    blocks: model.blocks,
    issueCount: model.issues.length,
    issues: model.issues,
    puzzleCount: model.puzzles.length,
    wordCount: model.puzzles.reduce((total, puzzle) => total + puzzle.words.length, 0),
  };
}

export function parseThematicContent(content) {
  const lines = String(content || "").split(/\r?\n/);
  const issues = [];
  const blocks = [];
  const puzzles = [];
  let currentBlock = null;
  let activeBlockName = "";
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
        activeBlockName = currentBlock.name;
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
      currentPuzzle = { blockName: activeBlockName, line: index + 1, title: "", fact: "", words: [] };
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
      if (currentPuzzle) {
        puzzles.push({
          blockName: currentPuzzle.blockName,
          fact: currentPuzzle.fact,
          title: currentPuzzle.title,
          words: currentPuzzle.words,
        });
      }
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
    blocks,
    issues,
    puzzles,
  };
}

export function serializeThematicContent(model) {
  const blocks = model.blocks?.length ? model.blocks : [{ name: "Default", slug: "default" }];
  const puzzles = model.puzzles || [];
  const lines = [];

  blocks.forEach((block) => {
    lines.push("[Block]");
    lines.push(`name: ${block.name || "Default"}`);
    lines.push("[/Block]");
    lines.push("");

    const blockPuzzles = puzzles.filter((puzzle) => (puzzle.blockName || "Default") === block.name);
    blockPuzzles.forEach((puzzle) => {
      lines.push("[Puzzle]");
      lines.push(`title: ${puzzle.title || "Nuevo puzzle"}`);
      lines.push(`fact: ${puzzle.fact || "Escribe aqui un dato breve."}`);
      lines.push("words:");
      for (const word of puzzle.words || []) {
        if (String(word).trim()) {
          lines.push(String(word).trim());
        }
      }
      lines.push("[/Puzzle]");
      lines.push("");
    });
  });

  return `${lines.join("\n").trim()}\n`;
}

export function createEmptyContentModel() {
  return {
    blocks: [{ name: "Nuevo bloque", slug: "nuevo_bloque" }],
    issues: [],
    puzzles: [
      {
        blockName: "Nuevo bloque",
        fact: "Escribe aqui un dato breve para este puzzle.",
        title: "Nuevo puzzle",
        words: ["PALABRA", "SEGUNDA", "TERCERA"],
      },
    ],
  };
}
