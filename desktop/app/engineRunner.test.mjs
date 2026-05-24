import assert from "node:assert/strict";
import { buildSimulatedGenerateOutput, consumeJsonLines, createStaticEngineRunner } from "./engineRunner.js";

const project = {
  book_title: "Ancient Egypt Word Search",
  input_path: "wordlists/egypt.txt",
  difficulty: "medium",
  grid_size: 14,
  limit: 4,
  output_dir: "output_puzzles_kdp/ancient_egypt",
};

const generatedOutput = buildSimulatedGenerateOutput(project);
assert.match(generatedOutput, /"type":"event"/);
assert.match(generatedOutput, /"total":4/);
assert.match(generatedOutput, /output_puzzles_kdp\/ancient_egypt\/book.pdf/);

const consumedEvents = [];
const consumedResult = await consumeJsonLines(generatedOutput, {
  onEvent: (event) => consumedEvents.push(event),
});

assert.equal(consumedEvents.length, 5);
assert.equal(consumedEvents.at(-1).type, "run_completed");
assert.deepEqual(consumedResult, { ok: true, pdf_path: "output_puzzles_kdp/ancient_egypt/book.pdf" });

const runnerEvents = [];
let runnerCommand = "";
const runner = createStaticEngineRunner({ delayMs: 0 });
const runnerResult = await runner.generate(project, {
  onCommand: (command) => {
    runnerCommand = command;
  },
  onEvent: (event) => runnerEvents.push(event),
});

assert.match(runnerCommand, /sopa-libros-engine project generate/);
assert.match(runnerCommand, /--json-lines/);
assert.equal(runnerEvents.length, 5);
assert.deepEqual(runnerResult, consumedResult);

console.log("desktop engine runner tests passed");
