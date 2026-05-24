import {
  buildProjectCommands,
  defaultProjectPath,
  projectToEngineRequest,
} from "./engineBridge.js";
import { createStaticEngineRunner } from "./engineRunner.js";

const demoProject = {
  schema_version: 1,
  project_type: "thematic",
  book_title: "Ancient Egypt Word Search",
  input_path: "wordlists/book_block.txt",
  difficulty: "medium",
  grid_size: 14,
  seed: 1234,
  theme_name: "premium-neutral",
  format_name: "trade-6x9",
  theme_manifest_path: "assets/generated/egypt/asset_manifest.json",
  output_dir: "output_puzzles_kdp/ancient_egypt",
  limit: 5,
  preview: true,
};

const sampleWords = ["NILE", "PYRAMID", "PHARAOH", "SCARAB", "TEMPLE", "SCRIBE"];
const sampleLetters = "NILEPYRAMIDPHARAOHSCARABTEMPLESCRIBEANKHOSIRISRAHORUS".repeat(2);
let project = { ...demoProject };
let selectedDifficulty = project.difficulty;
const engineRunner = createStaticEngineRunner();

const fields = {
  title: document.querySelector("#book-title"),
  inputPath: document.querySelector("#input-path"),
  themeManifest: document.querySelector("#theme-manifest"),
  outputDir: document.querySelector("#output-dir"),
  gridSize: document.querySelector("#grid-size"),
  seed: document.querySelector("#seed"),
  limit: document.querySelector("#limit"),
  themeName: document.querySelector("#theme-name"),
  formatName: document.querySelector("#format-name"),
  preview: document.querySelector("#preview"),
};

const els = {
  pageTitle: document.querySelector("#page-title"),
  projectJson: document.querySelector("#project-json"),
  requestJson: document.querySelector("#request-json"),
  validateCommand: document.querySelector("#validate-command"),
  generateCommand: document.querySelector("#generate-command"),
  previewTitle: document.querySelector("#preview-title"),
  previewGrid: document.querySelector("#preview-grid"),
  previewWords: document.querySelector("#preview-words"),
  eventList: document.querySelector("#event-list"),
  simulateRun: document.querySelector("#simulate-run"),
  toast: document.querySelector("#toast"),
};

function toNullableString(value) {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
}

function toNullableNumber(value) {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function toProjectFromForm() {
  return {
    schema_version: 1,
    project_type: "thematic",
    book_title: fields.title.value.trim() || "Untitled Word Search",
    input_path: fields.inputPath.value.trim(),
    difficulty: selectedDifficulty,
    grid_size: Number(fields.gridSize.value || 14),
    seed: toNullableNumber(fields.seed.value),
    theme_name: fields.themeName.value,
    format_name: fields.formatName.value,
    theme_manifest_path: toNullableString(fields.themeManifest.value),
    output_dir: toNullableString(fields.outputDir.value),
    limit: toNullableNumber(fields.limit.value),
    preview: fields.preview.checked,
  };
}

function toRequest(projectPayload) {
  return projectToEngineRequest(projectPayload);
}

function hydrateForm(nextProject) {
  project = { ...nextProject };
  selectedDifficulty = project.difficulty;
  fields.title.value = project.book_title;
  fields.inputPath.value = project.input_path;
  fields.themeManifest.value = project.theme_manifest_path || "";
  fields.outputDir.value = project.output_dir || "";
  fields.gridSize.value = project.grid_size;
  fields.seed.value = project.seed ?? "";
  fields.limit.value = project.limit ?? "";
  fields.themeName.value = project.theme_name;
  fields.formatName.value = project.format_name;
  fields.preview.checked = project.preview;
  syncDifficultyButtons();
  render();
}

function syncDifficultyButtons() {
  document.querySelectorAll("[data-difficulty]").forEach((button) => {
    button.classList.toggle("is-selected", button.dataset.difficulty === selectedDifficulty);
  });
}

function renderGrid() {
  els.previewGrid.innerHTML = "";
  const size = 10;
  els.previewGrid.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
  for (let index = 0; index < size * size; index += 1) {
    const cell = document.createElement("span");
    cell.textContent = sampleLetters[index % sampleLetters.length];
    els.previewGrid.appendChild(cell);
  }
}

function renderWords() {
  els.previewWords.innerHTML = "";
  sampleWords.forEach((word) => {
    const pill = document.createElement("span");
    pill.textContent = word;
    els.previewWords.appendChild(pill);
  });
}

function render() {
  project = toProjectFromForm();
  const request = toRequest(project);
  const projectPath = defaultProjectPath(project);
  const commands = buildProjectCommands(project, projectPath);
  els.pageTitle.textContent = project.book_title;
  els.previewTitle.textContent = project.book_title;
  els.projectJson.textContent = JSON.stringify(project, null, 2);
  els.requestJson.textContent = JSON.stringify(request, null, 2);
  els.validateCommand.textContent = commands.validate;
  els.generateCommand.textContent = commands.generate;
}

function showToast(message) {
  els.toast.textContent = message;
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => {
    els.toast.textContent = "";
  }, 2400);
}

function addEvent({ type, stage, message, current, total }) {
  const item = document.createElement("li");
  const eventType = document.createElement("span");
  const eventStage = document.createElement("span");
  const eventProgress = document.createElement("span");
  eventType.className = "event-type";
  eventStage.className = "event-stage";
  eventProgress.className = "event-progress";
  eventType.textContent = type;
  eventStage.textContent = `${stage}: ${message}`;
  eventProgress.textContent = total ? `${current || 0}/${total}` : "";
  item.append(eventType, eventStage, eventProgress);
  els.eventList.appendChild(item);
}

async function simulateRun() {
  els.eventList.innerHTML = "";
  els.simulateRun.disabled = true;
  try {
    const result = await engineRunner.generate(project, {
      onEvent: addEvent,
      onResult: (payload) => showToast(payload.ok ? `Generated ${payload.pdf_path}` : "Run failed."),
    });
    if (!result?.ok) {
      showToast("Run finished without a generated PDF.");
    }
  } finally {
    els.simulateRun.disabled = false;
  }
}

document.querySelectorAll("[data-panel]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-panel]").forEach((nav) => nav.classList.remove("is-active"));
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("is-visible"));
    button.classList.add("is-active");
    document.querySelector(`#${button.dataset.panel}`).classList.add("is-visible");
  });
});

document.querySelectorAll("[data-difficulty]").forEach((button) => {
  button.addEventListener("click", () => {
    selectedDifficulty = button.dataset.difficulty;
    syncDifficultyButtons();
    render();
  });
});

document.querySelector("#project-form").addEventListener("input", render);
document.querySelector("#reset-demo").addEventListener("click", () => hydrateForm(demoProject));
document.querySelector("#simulate-run").addEventListener("click", simulateRun);
document.querySelector("#clear-events").addEventListener("click", () => {
  els.eventList.innerHTML = "";
});
document.querySelector("#copy-project").addEventListener("click", async () => {
  const payload = JSON.stringify(project, null, 2);
  try {
    await navigator.clipboard.writeText(payload);
    showToast("Project JSON copied.");
  } catch {
    showToast("Clipboard unavailable in this preview.");
  }
});

renderGrid();
renderWords();
hydrateForm(project);
