import { useMemo, useState } from "react";
import { buildProjectCommands } from "../app/engineBridge.js";
import { DocumentStatus } from "./components/DocumentStatus.jsx";
import { PreviewRail } from "./components/PreviewRail.jsx";
import { ProjectPanel } from "./components/ProjectPanel.jsx";
import { RequestPanel } from "./components/RequestPanel.jsx";
import { RunPanel } from "./components/RunPanel.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import { useEngineRuntime } from "./hooks/useEngineRuntime.js";
import { useProjectDocument } from "./hooks/useProjectDocument.js";
import { useProjectFileActions } from "./hooks/useProjectFileActions.js";
import { useProjectRun } from "./hooks/useProjectRun.js";

export default function App() {
  const [activePanel, setActivePanel] = useState("project-panel");
  const [toast, setToast] = useState("");
  const projectDocument = useProjectDocument();
  const { runtimeLabel } = useEngineRuntime();
  const runState = useProjectRun(showToast);
  const fileActions = useProjectFileActions({
    markSaved: projectDocument.markSaved,
    projectJson: projectDocument.projectJson,
    projectPath: projectDocument.projectPath,
    showToast,
  });

  const commands = useMemo(
    () => buildProjectCommands(projectDocument.normalizedProject, projectDocument.projectPath),
    [projectDocument.normalizedProject, projectDocument.projectPath]
  );

  function showToast(message) {
    setToast(message);
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => setToast(""), 2400);
  }

  async function copyProject() {
    try {
      await navigator.clipboard.writeText(projectDocument.projectJson);
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
            <h2 id="page-title">{projectDocument.normalizedProject.book_title}</h2>
            <DocumentStatus isDirty={projectDocument.isDirty} projectPath={projectDocument.projectPath} />
          </div>
          <div className="topbar-actions">
            <button id="reset-demo" className="secondary-button" type="button" onClick={projectDocument.resetDemoProject}>
              Reset demo
            </button>
            <button
              id="save-project"
              className="secondary-button"
              type="button"
              onClick={fileActions.saveDraft}
              disabled={!fileActions.canSave || fileActions.isSaving}
            >
              {fileActions.isSaving ? "Saving..." : "Save draft"}
            </button>
            <button id="copy-project" className="primary-button" type="button" onClick={copyProject}>
              Copy project JSON
            </button>
          </div>
        </header>

        <ProjectPanel
          isVisible={activePanel === "project-panel"}
          project={projectDocument.project}
          setProject={projectDocument.setProject}
          validation={projectDocument.validation}
        />
        <RequestPanel
          isVisible={activePanel === "request-panel"}
          normalizedProject={projectDocument.normalizedProject}
          request={projectDocument.request}
        />
        <RunPanel
          commands={commands}
          events={runState.events}
          isRunning={runState.isRunning}
          isVisible={activePanel === "run-panel"}
          onClearEvents={runState.clearEvents}
          onSimulateRun={() => runState.simulateRun(projectDocument.normalizedProject)}
          validation={projectDocument.validation}
        />
      </main>

      <PreviewRail title={projectDocument.normalizedProject.book_title} toast={toast} />
    </div>
  );
}
