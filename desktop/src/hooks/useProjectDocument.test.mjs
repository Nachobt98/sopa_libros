import assert from "node:assert/strict";
import { defaultProjectPath } from "../../app/engineBridge.js";
import { demoProject, normalizeProject } from "../model/project.js";

const normalized = normalizeProject(demoProject);
assert.equal(defaultProjectPath(normalized), "projects/ancient_egypt_word_search.sopa.json");
assert.match(JSON.stringify(normalized, null, 2), /Ancient Egypt Word Search/);

console.log("desktop project document tests passed");
