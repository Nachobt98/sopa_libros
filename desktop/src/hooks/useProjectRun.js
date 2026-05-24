import { useState } from "react";
import { createStaticEngineRunner } from "../../app/engineRunner.js";

const engineRunner = createStaticEngineRunner();

export function useProjectRun(showToast) {
  const [events, setEvents] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  async function simulateRun(project) {
    setEvents([]);
    setIsRunning(true);
    try {
      const result = await engineRunner.generate(project, {
        onEvent: (event) => setEvents((current) => [...current, event]),
        onResult: (payload) => showToast(payload.ok ? `Generated ${payload.pdf_path}` : "Run failed."),
      });
      if (!result?.ok) {
        showToast("Run finished without a generated PDF.");
      }
    } finally {
      setIsRunning(false);
    }
  }

  return {
    events,
    isRunning,
    clearEvents: () => setEvents([]),
    simulateRun,
  };
}
