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
    return { path: payload.projectPath };
  },
});

assert.equal(bridge.isAvailable(), true);
assert.deepEqual(await bridge.saveProject("projects/demo.sopa.json", "{}"), { path: "projects/demo.sopa.json" });
assert.deepEqual(await bridge.readProject("projects/demo.sopa.json"), { book_title: "Demo" });
assert.deepEqual(calls, [
  { command: "save_project_file", payload: { projectPath: "projects/demo.sopa.json", contents: "{}" } },
  { command: "read_project_file", payload: { projectPath: "projects/demo.sopa.json" } },
]);

console.log("desktop project file bridge tests passed");
