import { useState } from "react";
import { createTauriEngineRunner } from "../../app/tauriEngineBridge.js";

const tauriEngineRunner = createTauriEngineRunner();

export function useProjectAssets(showToast, { markSaved, projectPath, saveDraft, setProject } = {}) {
  const [assetResult, setAssetResult] = useState(null);
  const [isBuildingAssets, setIsBuildingAssets] = useState(false);
  const isRealEngineAvailable = tauriEngineRunner.isAvailable();

  async function buildUserAssets(project, options) {
    setIsBuildingAssets(true);
    setAssetResult(null);
    try {
      if (!isRealEngineAvailable) {
        throw new Error("Asset generation requires the desktop runtime.");
      }
      if (!options.userAssetsDir?.trim()) {
        throw new Error("User assets folder is required.");
      }

      await saveDraft?.();
      const result = await tauriEngineRunner.buildUserAssets(project, options, { projectPath });
      if (result.project) {
        setProject?.(result.project);
        markSaved?.(result.project);
      }
      setAssetResult(result);
      showToast?.(`Asset manifest ready: ${result.assets?.manifest_path || "created"}`);
      return result;
    } catch (error) {
      const message = error.message || "Asset manifest build failed.";
      setAssetResult({ ok: false, error: message });
      showToast?.(message);
      throw error;
    } finally {
      setIsBuildingAssets(false);
    }
  }

  return {
    assetResult,
    buildUserAssets,
    isBuildingAssets,
    isRealEngineAvailable,
  };
}
