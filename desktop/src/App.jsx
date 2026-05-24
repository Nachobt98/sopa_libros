import { useMemo, useState } from "react";
import { buildProjectCommands } from "../app/engineBridge.js";
import { AssetsPanel } from "./components/AssetsPanel.jsx";
import { DocumentStatus } from "./components/DocumentStatus.jsx";
import { PreviewRail } from "./components/PreviewRail.jsx";
import { ProjectPanel } from "./components/ProjectPanel.jsx";
import { RequestPanel } from "./components/RequestPanel.jsx";
import { RunPanel } from "./components/RunPanel.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import { useEngineRuntime } from "./hooks/useEngineRuntime.js";
import { useProjectAssets } from "./hooks/useProjectAssets.js";
import { useProjectDocument } from "./hooks/useProjectDocument.js";
import { useProjectFileActions } from "./hooks/useProjectFileActions.js";
import { useProjectRun } from "./hooks/useProjectRun.js";

export default function App() {
  const [activePanel, setActivePanel] = useState("project-panel");
  const [toast, setToast] = useState("");
  const projectDocument = useProjectDocument();
  const { runtimeLabel } = useEngineRuntime();
  const fileActions = useProjectFileActions({
    loadProject: projectDocument.loadProject,
    markSaved: projectDocument.markSaved,
    projectJson: projectDocument.projectJson,
    projectPath: projectDocument.projectPath,
    showToast,
  });
  const runState = useProjectRun(showToast, {
    projectPath: projectDocument.projectPath,
    saveDraft: fileActions.saveDraft,
  });
  const assetState = useProjectAssets(showToast, {
    markSaved: projectDocument.markSaved,
    projectPath: projectDocument.projectPath,
    saveDraft: fileActions.saveDraft,
    setProject: projectDocument.setProject,
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
            <label className="project-path-field">
              <span>Project path</span>
              <input
                id="project-path"
                name="projectPath"
                type="text"
                value={projectDocument.projectPath}
                onChange={(event) => projectDocument.setProjectPath(event.target.value)}
              />
            </label>
            <button
              id="open-project"
              className="secondary-button"
              type="button"
              onClick={fileActions.openProject}
              disabled={!fileActions.canLoad || fileActions.isLoading}
            >
              {fileActions.isLoading ? "Opening..." : "Open"}
            </button>
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
        <AssetsPanel
          assetResult={assetState.assetResult}
          isBuildingAssets={assetState.isBuildingAssets}
          isRealEngineAvailable={assetState.isRealEngineAvailable}
          isVisible={activePanel === "assets-panel"}
          onBuildUserAssets={(options) => assetState.buildUserAssets(projectDocument.normalizedProject, options)}
          project={projectDocument.normalizedProject}
          validation={projectDocument.validation}
        />
        <RunPanel
          commands={commands}
          events={runState.events}
          isRealEngineAvailable={runState.isRealEngineAvailable}
          isRunning={runState.isRunning}
          isVisible={activePanel === "run-panel"}
          onClearEvents={runState.clearEvents}
          onGenerateProject={() => runState.generateProject(projectDocument.normalizedProject)}
          onValidateProject={() => runState.validateProject(projectDocument.normalizedProject)}
          runningAction={runState.runningAction}
          validation={projectDocument.validation}
        />
      </main>

      <PreviewRail title={projectDocument.normalizedProject.book_title} toast={toast} />
    </div>
  );
}
