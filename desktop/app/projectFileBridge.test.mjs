import assert from "node:assert/strict";
import { createProjectFileBridge } from "./projectFileBridge.js";

const unavailable = createProjectFileBridge({ invoke: null });
assert.equal(unavailable.isAvailable(), false);
await assert.rejects(() => unavailable.saveProject("projects/demo.sopa.json", "{}"), /Tauri invoke API is unavailable/);

const calls = [];
const bridge = createProjectFileBridge({
  invoke: async (command, payload) => {
    calls.push({ command, payload });
    if (command === "read_project_file") {
      return '{"book_title":"Demo"}';
    }
    if (command === "read_text_file") {
      return "[Puzzle]\ntitle: Demo\n[/Puzzle]\n";
    }
    return { path: payload.projectPath || payload.path };
  },
});

assert.equal(bridge.isAvailable(), true);
assert.deepEqual(await bridge.saveProject("projects/demo.sopa.json", "{}"), { path: "projects/demo.sopa.json" });
assert.deepEqual(await bridge.readProject("projects/demo.sopa.json"), { book_title: "Demo" });
assert.deepEqual(await bridge.saveText("wordlists/demo.txt", "content"), { path: "wordlists/demo.txt" });
assert.equal(await bridge.readText("wordlists/demo.txt"), "[Puzzle]\ntitle: Demo\n[/Puzzle]\n");
assert.deepEqual(calls, [
  { command: "save_project_file", payload: { projectPath: "projects/demo.sopa.json", contents: "{}" } },
  { command: "read_project_file", payload: { projectPath: "projects/demo.sopa.json" } },
  { command: "save_text_file", payload: { path: "wordlists/demo.txt", contents: "content" } },
  { command: "read_text_file", payload: { path: "wordlists/demo.txt" } },
]);

console.log("desktop project file bridge tests passed");
