import assert from "node:assert/strict";
import {
  analyzeThematicContent,
  parseThematicContent,
  serializeThematicContent,
  slugifyName,
  starterContentTemplate,
} from "./contentAnalysis.js";

assert.equal(slugifyName("Ancient Egypt"), "ancient_egypt");
assert.equal(slugifyName("  "), "default");

const analysis = analyzeThematicContent(starterContentTemplate);
assert.equal(analysis.blockCount, 1);
assert.equal(analysis.blocks[0].slug, "ancient_egypt");
assert.equal(analysis.puzzleCount, 1);
assert.equal(analysis.wordCount, 6);
assert.equal(analysis.issueCount, 0);
const model = parseThematicContent(starterContentTemplate);
assert.equal(model.puzzles[0].title, "Pharaohs and Queens");
assert.equal(model.puzzles[0].blockName, "Ancient Egypt");
assert.match(serializeThematicContent(model), /\[Puzzle\]/);

const broken = analyzeThematicContent("[Puzzle]\nwords:\nONLYWORD\n");
assert.equal(broken.puzzleCount, 0);
assert.equal(broken.issueCount, 1);
assert.match(broken.issues[0].message, /cierre/);

console.log("desktop content analysis tests passed");
