import { useMemo, useState } from "react";
import { createProjectFileBridge } from "../../app/projectFileBridge.js";

export function useProjectFileActions({ loadProject, markSaved, projectJson, projectPath, showToast }) {
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const projectFileBridge = useMemo(() => createProjectFileBridge(), []);

  async function saveDraft() {
    setIsSaving(true);
    try {
      const output = await projectFileBridge.saveProject(projectPath, projectJson);
      markSaved();
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

  return {
    canLoad: projectFileBridge.isAvailable(),
    canSave: projectFileBridge.isAvailable(),
    isLoading,
    isSaving,
    openProject,
    saveDraft,
  };
}
