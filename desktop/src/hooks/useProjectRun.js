import { useState } from "react";
import { createStaticEngineRunner } from "../../app/engineRunner.js";
import { createTauriEngineRunner } from "../../app/tauriEngineBridge.js";

const staticEngineRunner = createStaticEngineRunner();
const tauriEngineRunner = createTauriEngineRunner();

export function useProjectRun(showToast, { projectPath, saveDraft } = {}) {
  const [events, setEvents] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [runningAction, setRunningAction] = useState(null);
  const isRealEngineAvailable = tauriEngineRunner.isAvailable();

  function addEvent(event) {
    setEvents((current) => [...current, event]);
  }

  async function ensureSaved() {
    if (isRealEngineAvailable && saveDraft) {
      await saveDraft();
    }
  }

  async function validateProject(project) {
    setEvents([]);
    setIsRunning(true);
    setRunningAction("validate");
    try {
      addEvent({ type: "stage_started", stage: "validation", message: "Validating project file." });
      if (isRealEngineAvailable) {
        await ensureSaved();
        const result = await tauriEngineRunner.validate(project, { projectPath });
        addEvent({
          type: result.ok ? "stage_completed" : "stage_failed",
          stage: "validation",
          message: result.ok ? "Project validation completed." : "Project validation failed.",
        });
        showToast(result.ok ? "Project is valid." : "Project has validation issues.");
      } else {
        addEvent({ type: "stage_completed", stage: "validation", message: "Browser preview validation completed." });
        showToast("Project is valid for browser preview.");
      }
    } catch (error) {
      addEvent({ type: "stage_failed", stage: "validation", message: error.message || "Project validation failed." });
      showToast(error.message || "Project validation failed.");
    } finally {
      setIsRunning(false);
      setRunningAction(null);
    }
  }

  async function generateProject(project) {
    setEvents([]);
    setIsRunning(true);
    setRunningAction("generate");
    try {
      if (isRealEngineAvailable) {
        await ensureSaved();
      }
      const runner = isRealEngineAvailable ? tauriEngineRunner : staticEngineRunner;
      const result = await runner.generate(project, {
        projectPath,
        onEvent: addEvent,
        onResult: (payload) => showToast(payload.ok ? `Generated ${payload.pdf_path}` : "Run failed."),
      });
      if (!result?.ok) {
        showToast("Run finished without a generated PDF.");
      }
    } catch (error) {
      addEvent({ type: "stage_failed", stage: "generation", message: error.message || "Generation failed." });
      showToast(error.message || "Generation failed.");
    } finally {
      setIsRunning(false);
      setRunningAction(null);
    }
  }

  return {
    events,
    isRealEngineAvailable,
    isRunning,
    runningAction,
    clearEvents: () => setEvents([]),
    generateProject,
    validateProject,
  };
}
