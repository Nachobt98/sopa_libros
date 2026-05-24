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
const invokedPayloads = [];
const runner = createTauriEngineRunner({
  invoke: async (command, payload) => {
    assert.equal(command, "run_engine_project_command");
    invokedPayloads.push(payload);
    if (payload.mode === "validate") {
      return {
        ok: true,
        status_code: 0,
        stderr: "",
        stdout: '{"ok":true,"issues":[]}',
      };
    }
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

const assetPayloads = [];
const assetRunner = createTauriEngineRunner({
  invoke: async (command, payload) => {
    assert.equal(command, "run_engine_project_assets_command");
    assetPayloads.push(payload);
    return {
      ok: true,
      status_code: 0,
      stderr: "",
      stdout: JSON.stringify({
        ok: true,
        command: "project.assets",
        project: {
          book_title: "Ancient Egypt Word Search",
          theme_manifest_path: "assets/generated/egypt-user/asset_manifest.json",
        },
        assets: {
          manifest_path: "assets/generated/egypt-user/asset_manifest.json",
          asset_count: 3,
        },
      }),
    };
  },
});

const validationResult = await runner.validate({ book_title: "Ancient Egypt Word Search" });
const result = await runner.generate(
  { book_title: "Ancient Egypt Word Search" },
  { onEvent: (event) => runnerEvents.push(event) }
);

assert.equal(runner.isAvailable(), true);
assert.deepEqual(validationResult, { ok: true, issues: [] });
assert.deepEqual(invokedPayloads, [
  {
    mode: "validate",
    projectPath: "projects/ancient_egypt_word_search.sopa.json",
  },
  {
    mode: "generate",
    projectPath: "projects/ancient_egypt_word_search.sopa.json",
  },
]);
assert.equal(runnerEvents.length, 1);
assert.deepEqual(result, { ok: true, pdf_path: "out/book.pdf" });

const assetResult = await assetRunner.buildUserAssets(
  { book_title: "Ancient Egypt Word Search" },
  {
    userAssetsDir: "assets/user/egypt",
    outputDir: "assets/generated/egypt-user",
    style: "reviewed-user-assets",
  }
);

assert.deepEqual(assetPayloads, [
  {
    projectPath: "projects/ancient_egypt_word_search.sopa.json",
    userAssetsDir: "assets/user/egypt",
    outputDir: "assets/generated/egypt-user",
    style: "reviewed-user-assets",
  },
]);
assert.equal(assetResult.assets.manifest_path, "assets/generated/egypt-user/asset_manifest.json");

console.log("desktop tauri engine bridge tests passed");
