import { defaultProjectPath } from "./engineBridge.js";
import { consumeJsonLines } from "./engineRunner.js";

export function getTauriInvoke(globalObject = globalThis) {
  return globalObject.__TAURI__?.core?.invoke || null;
}

export async function loadEngineRuntimeStatus({ invoke = getTauriInvoke() } = {}) {
  if (!invoke) {
    return {
      available: false,
      engineFound: false,
      engineCommand: "sopa-libros-engine",
      currentDir: "",
    };
  }

  const status = await invoke("engine_runtime_status");
  return {
    available: true,
    engineFound: Boolean(status.engine_found),
    engineCommand: status.engine_command,
    currentDir: status.current_dir,
  };
}

export function createTauriEngineRunner({ invoke = getTauriInvoke() } = {}) {
  async function runProjectCommand(mode, projectPath) {
    const output = await invoke("run_engine_project_command", {
      mode,
      projectPath,
    });

    if (!output.ok) {
      throw new Error(output.stderr || output.stdout || `Engine exited with status ${output.status_code ?? "unknown"}.`);
    }

    return output;
  }

  return {
    isAvailable() {
      return Boolean(invoke);
    },

    async validate(project, handlers = {}) {
      if (!invoke) {
        throw new Error("Tauri invoke API is unavailable.");
      }

      const projectPath = handlers.projectPath || defaultProjectPath(project);
      handlers.onCommand?.(`sopa-libros-engine project validate --project ${projectPath}`);
      const output = await runProjectCommand("validate", projectPath);

      if (output.stderr) {
        handlers.onStderr?.(output.stderr);
      }

      const result = JSON.parse(output.stdout || "{}");
      handlers.onResult?.(result);
      return result;
    },

    async generate(project, handlers = {}) {
      if (!invoke) {
        throw new Error("Tauri invoke API is unavailable.");
      }

      const projectPath = handlers.projectPath || defaultProjectPath(project);
      handlers.onCommand?.(`sopa-libros-engine project generate --project ${projectPath} --json-lines`);
      const output = await runProjectCommand("generate", projectPath);

      if (output.stderr) {
        handlers.onStderr?.(output.stderr);
      }

      const result = await consumeJsonLines(output.stdout, handlers);
      return result;
    },
  };
}
