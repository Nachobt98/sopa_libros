import { useEffect, useMemo, useState } from "react";
import { buildProjectCommands, defaultProjectPath, projectToEngineRequest } from "../app/engineBridge.js";
import { createStaticEngineRunner } from "../app/engineRunner.js";
import { loadEngineRuntimeStatus } from "../app/tauriEngineBridge.js";

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
const engineRunner = createStaticEngineRunner();

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

function normalizeProject(project) {
  return {
    ...project,
    book_title: project.book_title.trim() || "Untitled Word Search",
    input_path: project.input_path.trim(),
    grid_size: Number(project.grid_size || 14),
    seed: toNullableNumber(project.seed),
    theme_manifest_path: toNullableString(project.theme_manifest_path),
    output_dir: toNullableString(project.output_dir),
    limit: toNullableNumber(project.limit),
  };
}

function GridPreview() {
  return (
    <div id="preview-grid" className="preview-grid" aria-hidden="true">
      {Array.from({ length: 100 }, (_, index) => (
        <span key={index}>{sampleLetters[index % sampleLetters.length]}</span>
      ))}
    </div>
  );
}

function WordsPreview() {
  return (
    <div id="preview-words" className="preview-words">
      {sampleWords.map((word) => (
        <span key={word}>{word}</span>
      ))}
    </div>
  );
}

function ProjectForm({ project, setProject }) {
  function updateField(field, value) {
    setProject((current) => ({ ...current, [field]: value }));
  }

  return (
    <form id="project-form" className="editor-grid">
      <label>
        <span>Book title</span>
        <input
          id="book-title"
          name="bookTitle"
          type="text"
          autoComplete="off"
          value={project.book_title}
          onChange={(event) => updateField("book_title", event.target.value)}
        />
      </label>

      <label>
        <span>Thematic TXT input</span>
        <input
          id="input-path"
          name="inputPath"
          type="text"
          autoComplete="off"
          value={project.input_path}
          onChange={(event) => updateField("input_path", event.target.value)}
        />
      </label>

      <label>
        <span>Theme manifest</span>
        <input
          id="theme-manifest"
          name="themeManifestPath"
          type="text"
          autoComplete="off"
          value={project.theme_manifest_path || ""}
          onChange={(event) => updateField("theme_manifest_path", event.target.value)}
        />
      </label>

      <label>
        <span>Output directory</span>
        <input
          id="output-dir"
          name="outputDir"
          type="text"
          autoComplete="off"
          value={project.output_dir || ""}
          onChange={(event) => updateField("output_dir", event.target.value)}
        />
      </label>

      <fieldset className="segmented-field">
        <legend>Difficulty</legend>
        <div className="segmented" role="radiogroup" aria-label="Difficulty">
          {["easy", "medium", "hard"].map((difficulty) => (
            <button
              key={difficulty}
              type="button"
              className={project.difficulty === difficulty ? "is-selected" : ""}
              onClick={() => updateField("difficulty", difficulty)}
            >
              {difficulty[0].toUpperCase() + difficulty.slice(1)}
            </button>
          ))}
        </div>
      </fieldset>

      <label>
        <span>Grid size</span>
        <input
          id="grid-size"
          name="gridSize"
          type="number"
          min="6"
          max="30"
          step="1"
          value={project.grid_size}
          onChange={(event) => updateField("grid_size", event.target.value)}
        />
      </label>

      <label>
        <span>Seed</span>
        <input
          id="seed"
          name="seed"
          type="number"
          step="1"
          value={project.seed ?? ""}
          onChange={(event) => updateField("seed", event.target.value)}
        />
      </label>

      <label>
        <span>Puzzle limit</span>
        <input
          id="limit"
          name="limit"
          type="number"
          min="1"
          step="1"
          value={project.limit ?? ""}
          onChange={(event) => updateField("limit", event.target.value)}
        />
      </label>

      <label>
        <span>Theme</span>
        <select
          id="theme-name"
          name="themeName"
          value={project.theme_name}
          onChange={(event) => updateField("theme_name", event.target.value)}
        >
          <option value="current-default">Current default</option>
          <option value="premium-neutral">Premium neutral</option>
          <option value="bold-modern">Bold modern</option>
          <option value="kids">Kids</option>
        </select>
      </label>

      <label>
        <span>Format</span>
        <select
          id="format-name"
          name="formatName"
          value={project.format_name}
          onChange={(event) => updateField("format_name", event.target.value)}
        >
          <option value="trade-6x9">Trade 6 x 9</option>
          <option value="activity-8.5x11">Activity 8.5 x 11</option>
          <option value="large-print-8x10">Large print 8 x 10</option>
          <option value="square-8.5">Square 8.5</option>
        </select>
      </label>

      <label className="toggle-row">
        <input
          id="preview"
          name="preview"
          type="checkbox"
          checked={project.preview}
          onChange={(event) => updateField("preview", event.target.checked)}
        />
        <span>Preview mode</span>
      </label>
    </form>
  );
}

function EventList({ events }) {
  return (
    <ol id="event-list" className="event-list" aria-live="polite">
      {events.map((event, index) => (
        <li key={`${event.type}-${event.stage}-${index}`}>
          <span className="event-type">{event.type}</span>
          <span className="event-stage">
            {event.stage}: {event.message}
          </span>
          <span className="event-progress">{event.total ? `${event.current || 0}/${event.total}` : ""}</span>
        </li>
      ))}
    </ol>
  );
}

export default function App() {
  const [activePanel, setActivePanel] = useState("project-panel");
  const [project, setProject] = useState(demoProject);
  const [events, setEvents] = useState([]);
  const [toast, setToast] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [runtimeStatus, setRuntimeStatus] = useState({
    available: false,
    engineFound: false,
    engineCommand: "sopa-libros-engine",
    currentDir: "",
  });

  const normalizedProject = useMemo(() => normalizeProject(project), [project]);
  const request = useMemo(() => projectToEngineRequest(normalizedProject), [normalizedProject]);
  const commands = useMemo(() => buildProjectCommands(normalizedProject, defaultProjectPath(normalizedProject)), [normalizedProject]);
  const runtimeLabel = runtimeStatus.available
    ? `Tauri bridge ${runtimeStatus.engineFound ? "ready" : "missing engine"}`
    : "Browser preview";

  useEffect(() => {
    let isMounted = true;
    loadEngineRuntimeStatus()
      .then((status) => {
        if (isMounted) {
          setRuntimeStatus(status);
        }
      })
      .catch(() => {
        if (isMounted) {
          setRuntimeStatus((current) => ({ ...current, available: false, engineFound: false }));
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  function showToast(message) {
    setToast(message);
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => setToast(""), 2400);
  }

  async function simulateRun() {
    setEvents([]);
    setIsRunning(true);
    try {
      const result = await engineRunner.generate(normalizedProject, {
        onEvent: (event) => setEvents((current) => [...current, event]),
        onResult: (payload) => showToast(payload.ok ? `Generated ${payload.pdf_path}` : "Run failed."),
      });
      if (!result?.ok) {
        showToast("Run finished without a generated PDF.");
      }
    } finally {
      setIsRunning(false);
    }
  }

  async function copyProject() {
    const payload = JSON.stringify(normalizedProject, null, 2);
    try {
      await navigator.clipboard.writeText(payload);
      showToast("Project JSON copied.");
    } catch {
      showToast("Clipboard unavailable in this preview.");
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Project navigation">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            SL
          </div>
          <div>
            <h1>sopa-libros</h1>
            <p>KDP word search studio</p>
          </div>
        </div>

        <nav className="nav-stack" aria-label="Workflow">
          {[
            ["project-panel", "Project"],
            ["request-panel", "Request"],
            ["run-panel", "Run"],
          ].map(([panel, label]) => (
            <button
              key={panel}
              className={`nav-item ${activePanel === panel ? "is-active" : ""}`}
              type="button"
              onClick={() => setActivePanel(panel)}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="status-block">
          <span className="status-dot"></span>
          <span>{runtimeLabel}</span>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Project file</p>
            <h2 id="page-title">{normalizedProject.book_title}</h2>
          </div>
          <div className="topbar-actions">
            <button id="reset-demo" className="secondary-button" type="button" onClick={() => setProject(demoProject)}>
              Reset demo
            </button>
            <button id="copy-project" className="primary-button" type="button" onClick={copyProject}>
              Copy project JSON
            </button>
          </div>
        </header>

        <section id="project-panel" className={`panel ${activePanel === "project-panel" ? "is-visible" : ""}`} aria-labelledby="project-heading">
          <div className="section-heading">
            <h3 id="project-heading">Project Settings</h3>
            <p>These fields map to the `.sopa.json` project model.</p>
          </div>
          <ProjectForm project={project} setProject={setProject} />
        </section>

        <section id="request-panel" className={`panel ${activePanel === "request-panel" ? "is-visible" : ""}`} aria-labelledby="request-heading">
          <div className="section-heading">
            <h3 id="request-heading">Engine Request</h3>
            <p>The app will send this payload to `sopa-libros-engine`.</p>
          </div>
          <div className="split-grid">
            <div>
              <h4>Project JSON</h4>
              <pre id="project-json" className="code-pane">
                {JSON.stringify(normalizedProject, null, 2)}
              </pre>
            </div>
            <div>
              <h4>Request JSON</h4>
              <pre id="request-json" className="code-pane">
                {JSON.stringify(request, null, 2)}
              </pre>
            </div>
          </div>
        </section>

        <section id="run-panel" className={`panel ${activePanel === "run-panel" ? "is-visible" : ""}`} aria-labelledby="run-heading">
          <div className="section-heading">
            <h3 id="run-heading">Run Preview</h3>
            <p>Shows how progress will flow from JSON Lines.</p>
          </div>

          <div className="command-grid">
            <div>
              <h4>Validate</h4>
              <code id="validate-command">{commands.validate}</code>
            </div>
            <div>
              <h4>Generate</h4>
              <code id="generate-command">{commands.generate}</code>
            </div>
          </div>

          <div className="run-toolbar">
            <button id="simulate-run" className="primary-button" type="button" onClick={simulateRun} disabled={isRunning}>
              {isRunning ? "Running..." : "Simulate run"}
            </button>
            <button id="clear-events" className="secondary-button" type="button" onClick={() => setEvents([])}>
              Clear events
            </button>
          </div>

          <EventList events={events} />
        </section>
      </main>

      <aside className="preview-rail" aria-label="Book preview">
        <div className="book-preview">
          <div className="page-preview">
            <div className="page-label">Puzzle 01</div>
            <div id="preview-title" className="preview-title">
              {normalizedProject.book_title}
            </div>
            <GridPreview />
            <WordsPreview />
          </div>
        </div>
        <div id="toast" className="toast" role="status" aria-live="polite">
          {toast}
        </div>
      </aside>
    </div>
  );
}
