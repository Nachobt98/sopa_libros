import { useEffect, useState } from "react";
import { loadEngineRuntimeStatus } from "../../app/tauriEngineBridge.js";

const defaultRuntimeStatus = {
  available: false,
  engineFound: false,
  engineCommand: "sopa-libros-engine",
  currentDir: "",
};

export function useEngineRuntime() {
  const [runtimeStatus, setRuntimeStatus] = useState(defaultRuntimeStatus);

  useEffect(() => {
    let isMounted = true;
    loadEngineRuntimeStatus()
      .then((status) => {
        if (isMounted) {
          setRuntimeStatus(status);
        }
      })
      .catch(() => {
        if (isMounted) {
          setRuntimeStatus((current) => ({ ...current, available: false, engineFound: false }));
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const runtimeLabel = runtimeStatus.available
    ? `Tauri bridge ${runtimeStatus.engineFound ? "ready" : "missing engine"}`
    : "Browser preview";

  return { runtimeStatus, runtimeLabel };
}
