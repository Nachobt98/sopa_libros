import { getTauriInvoke } from "./tauriEngineBridge.js";

export function createProjectFileBridge({ invoke = getTauriInvoke() } = {}) {
  return {
    isAvailable() {
      return Boolean(invoke);
    },

    async saveProject(projectPath, contents) {
      if (!invoke) {
        throw new Error("Tauri invoke API is unavailable.");
      }
      return invoke("save_project_file", { projectPath, contents });
    },

    async readProject(projectPath) {
      if (!invoke) {
        throw new Error("Tauri invoke API is unavailable.");
      }
      const contents = await invoke("read_project_file", { projectPath });
      return JSON.parse(contents);
    },

    async saveText(path, contents) {
      if (!invoke) {
        throw new Error("Tauri invoke API is unavailable.");
      }
      return invoke("save_text_file", { path, contents });
    },

    async readText(path) {
      if (!invoke) {
        throw new Error("Tauri invoke API is unavailable.");
      }
      return invoke("read_text_file", { path });
    },
  };
}
