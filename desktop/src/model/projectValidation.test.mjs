import assert from "node:assert/strict";
import { demoProject } from "./project.js";
import { validateProject } from "./projectValidation.js";

assert.deepEqual(validateProject(demoProject), { ok: true, issues: [] });

const invalid = validateProject({
  ...demoProject,
  book_title: "",
  input_path: "",
  difficulty: "expert",
  grid_size: 4,
  limit: 0,
});

assert.equal(invalid.ok, false);
assert.deepEqual(
  invalid.issues.map((issue) => issue.field),
  ["book_title", "input_path", "difficulty", "grid_size", "limit"]
);

console.log("desktop project validation tests passed");
