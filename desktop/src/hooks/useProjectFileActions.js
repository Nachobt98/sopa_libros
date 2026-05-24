import { useMemo, useState } from "react";
import { createProjectFileBridge } from "../../app/projectFileBridge.js";

export function useProjectFileActions({ loadProject, markSaved, onProjectSaved, projectJson, projectPath, showToast }) {
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const projectFileBridge = useMemo(() => createProjectFileBridge(), []);

  async function saveDraft() {
    setIsSaving(true);
    try {
      const output = await projectFileBridge.saveProject(projectPath, projectJson);
      markSaved();
      onProjectSaved?.(JSON.parse(projectJson), output.path);
      if (showToast) {
        showToast(`Saved ${output.path}`);
      }
      return output;
    } catch (error) {
      if (showToast) {
        showToast(error.message || "Project save failed.");
      }
      throw error;
    } finally {
      setIsSaving(false);
    }
  }

  async function openProject() {
    setIsLoading(true);
    try {
      const project = await projectFileBridge.readProject(projectPath);
      loadProject(project, projectPath);
      onProjectSaved?.(project, projectPath);
      if (showToast) {
        showToast(`Opened ${projectPath}`);
      }
      return project;
    } catch (error) {
      if (showToast) {
        showToast(error.message || "Project open failed.");
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }

  async function openPath(path) {
    try {
      await projectFileBridge.openPath(path);
    } catch (error) {
      if (showToast) {
        showToast(error.message || "No se pudo abrir la ruta.");
      }
      throw error;
    }
  }

  return {
    canLoad: projectFileBridge.isAvailable(),
    canSave: projectFileBridge.isAvailable(),
    isLoading,
    isSaving,
    openProject,
    openPath,
    saveDraft,
  };
}
