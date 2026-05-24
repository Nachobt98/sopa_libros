import assert from "node:assert/strict";
import { createTauriEngineRunner, getTauriInvoke, loadEngineRuntimeStatus } from "./tauriEngineBridge.js";

assert.equal(getTauriInvoke({}), null);
assert.equal(typeof getTauriInvoke({ __TAURI__: { core: { invoke: () => null } } }), "function");

const unavailableStatus = await loadEngineRuntimeStatus({ invoke: null });
assert.deepEqual(unavailableStatus, {
  available: false,
  engineFound: false,
  engineCommand: "sopa-libros-engine",
  currentDir: "",
});

const availableStatus = await loadEngineRuntimeStatus({
  invoke: async (command) => {
    assert.equal(command, "engine_runtime_status");
    return {
      current_dir: "C:/workspace",
      engine_command: "sopa-libros-engine",
      engine_found: true,
    };
  },
});

assert.deepEqual(availableStatus, {
  available: true,
  engineFound: true,
  engineCommand: "sopa-libros-engine",
  currentDir: "C:/workspace",
});

const runnerEvents = [];
let invokedPayload = null;
const runner = createTauriEngineRunner({
  invoke: async (command, payload) => {
    assert.equal(command, "run_engine_project_command");
    invokedPayload = payload;
    return {
      ok: true,
      status_code: 0,
      stderr: "",
      stdout: [
        '{"type":"event","event":{"type":"stage_started","stage":"parsing","message":"Parsing."}}',
        '{"type":"result","result":{"ok":true,"pdf_path":"out/book.pdf"}}',
      ].join("\n"),
    };
  },
});

const result = await runner.generate(
  { book_title: "Ancient Egypt Word Search" },
  { onEvent: (event) => runnerEvents.push(event) }
);

assert.equal(runner.isAvailable(), true);
assert.deepEqual(invokedPayload, {
  mode: "generate",
  projectPath: "projects/ancient_egypt_word_search.sopa.json",
});
assert.equal(runnerEvents.length, 1);
assert.deepEqual(result, { ok: true, pdf_path: "out/book.pdf" });

console.log("desktop tauri engine bridge tests passed");
