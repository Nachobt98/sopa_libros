import assert from "node:assert/strict";
import {
  buildProjectCommands,
  defaultProjectPath,
  parseJsonLine,
  parseJsonLines,
  projectToEngineRequest,
  slugifyProjectName,
  summarizeJsonLines,
} from "./engineBridge.js";

const project = {
  schema_version: 1,
  project_type: "thematic",
  book_title: "Ancient Egypt Word Search",
  input_path: "wordlists/egypt.txt",
  difficulty: "medium",
  grid_size: 14,
};

assert.equal(slugifyProjectName("Ancient Egypt Word Search"), "ancient_egypt_word_search");
assert.equal(defaultProjectPath(project), "projects/ancient_egypt_word_search.sopa.json");

assert.deepEqual(projectToEngineRequest(project), {
  book_title: "Ancient Egypt Word Search",
  input_path: "wordlists/egypt.txt",
  difficulty: "medium",
  grid_size: 14,
});

assert.deepEqual(buildProjectCommands(project), {
  validate: "sopa-libros-engine project validate --project projects/ancient_egypt_word_search.sopa.json",
  generate:
    "sopa-libros-engine project generate --project projects/ancient_egypt_word_search.sopa.json --json-lines",
});

assert.equal(parseJsonLine(""), null);
assert.throws(() => parseJsonLine('{"type":"unknown"}'), /Unsupported JSON Lines payload type/);

const records = parseJsonLines(
  [
    '{"type":"event","event":{"type":"stage_started","stage":"parsing","message":"Parsing."}}',
    '{"type":"result","result":{"ok":true,"pdf_path":"out/book.pdf"}}',
  ].join("\n")
);
const summary = summarizeJsonLines(records);

assert.equal(summary.events.length, 1);
assert.equal(summary.events[0].stage, "parsing");
assert.deepEqual(summary.result, { ok: true, pdf_path: "out/book.pdf" });

console.log("desktop engine bridge tests passed");
