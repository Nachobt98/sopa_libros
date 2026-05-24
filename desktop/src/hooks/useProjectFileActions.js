import { useMemo, useState } from "react";
import { createProjectFileBridge } from "../../app/projectFileBridge.js";

export function useProjectFileActions({ markSaved, projectJson, projectPath, showToast }) {
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

  return {
    canSave: projectFileBridge.isAvailable(),
    isSaving,
    saveDraft,
  };
}
