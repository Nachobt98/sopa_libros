export function slugifyProjectName(value) {
  return String(value || "wordsearch_project")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

export function defaultProjectPath(project) {
  return `projects/${slugifyProjectName(project.book_title)}.sopa.json`;
}

export function projectToEngineRequest(project) {
  const { schema_version, project_type, ...request } = project;
  return request;
}

export function buildProjectCommands(project, projectPath = defaultProjectPath(project)) {
  return {
    validate: `sopa-libros-engine project validate --project ${projectPath}`,
    generate: `sopa-libros-engine project generate --project ${projectPath} --json-lines`,
  };
}

export function parseJsonLine(line) {
  const trimmed = String(line || "").trim();
  if (!trimmed) {
    return null;
  }
  const payload = JSON.parse(trimmed);
  if (payload.type !== "event" && payload.type !== "result") {
    throw new Error(`Unsupported JSON Lines payload type: ${payload.type}`);
  }
  return payload;
}

export function parseJsonLines(text) {
  return String(text || "")
    .split(/\r?\n/)
    .map(parseJsonLine)
    .filter(Boolean);
}

export function summarizeJsonLines(records) {
  const events = records.filter((record) => record.type === "event").map((record) => record.event);
  const result = [...records].reverse().find((record) => record.type === "result")?.result || null;
  return { events, result };
}
