import { useMemo, useState } from "react";
import { buildProjectCommands, defaultProjectPath, projectToEngineRequest } from "../app/engineBridge.js";
import { PreviewRail } from "./components/PreviewRail.jsx";
import { ProjectPanel } from "./components/ProjectPanel.jsx";
import { RequestPanel } from "./components/RequestPanel.jsx";
import { RunPanel } from "./components/RunPanel.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import { useEngineRuntime } from "./hooks/useEngineRuntime.js";
import { useProjectRun } from "./hooks/useProjectRun.js";
import { demoProject, normalizeProject } from "./model/project.js";
import { validateProject } from "./model/projectValidation.js";

export default function App() {
  const [activePanel, setActivePanel] = useState("project-panel");
  const [project, setProject] = useState(demoProject);
  const [toast, setToast] = useState("");
  const { runtimeLabel } = useEngineRuntime();
  const runState = useProjectRun(showToast);

  const normalizedProject = useMemo(() => normalizeProject(project), [project]);
  const validation = useMemo(() => validateProject(project), [project]);
  const request = useMemo(() => projectToEngineRequest(normalizedProject), [normalizedProject]);
  const commands = useMemo(() => buildProjectCommands(normalizedProject, defaultProjectPath(normalizedProject)), [normalizedProject]);

  function showToast(message) {
    setToast(message);
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => setToast(""), 2400);
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
      <Sidebar activePanel={activePanel} runtimeLabel={runtimeLabel} setActivePanel={setActivePanel} />

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

        <ProjectPanel
          isVisible={activePanel === "project-panel"}
          project={project}
          setProject={setProject}
          validation={validation}
        />
        <RequestPanel isVisible={activePanel === "request-panel"} normalizedProject={normalizedProject} request={request} />
        <RunPanel
          commands={commands}
          events={runState.events}
          isRunning={runState.isRunning}
          isVisible={activePanel === "run-panel"}
          onClearEvents={runState.clearEvents}
          onSimulateRun={() => runState.simulateRun(normalizedProject)}
          validation={validation}
        />
      </main>

      <PreviewRail title={normalizedProject.book_title} toast={toast} />
    </div>
  );
}
