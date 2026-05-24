import { buildProjectCommands, parseJsonLine } from "./engineBridge.js";

function wait(delayMs, setTimeoutFn) {
  if (!delayMs) {
    return Promise.resolve();
  }
  return new Promise((resolve) => setTimeoutFn(resolve, delayMs));
}

export function buildSimulatedGenerateOutput(project) {
  const total = project.limit || 5;
  const outputDir = project.output_dir || "output_puzzles_kdp";
  const pdfPath = `${outputDir.replace(/\/+$/, "")}/book.pdf`;
  const progressCurrent = Math.min(3, total);

  return [
    { type: "event", event: { type: "stage_started", stage: "parsing", message: "Parsing thematic input." } },
    { type: "event", event: { type: "stage_completed", stage: "validation", message: "Validation completed." } },
    {
      type: "event",
      event: {
        type: "progress",
        stage: "grid_generation",
        message: "Generated puzzle grid.",
        current: progressCurrent,
        total,
      },
    },
    {
      type: "event",
      event: {
        type: "progress",
        stage: "rendering",
        message: "Rendered puzzle page pair.",
        current: total,
        total,
      },
    },
    { type: "event", event: { type: "run_completed", stage: "complete", message: "Thematic generation completed." } },
    { type: "result", result: { ok: true, pdf_path: pdfPath } },
  ]
    .map((record) => JSON.stringify(record))
    .join("\n");
}

export async function consumeJsonLines(text, handlers = {}) {
  let finalResult = null;
  const lines = String(text || "").split(/\r?\n/);

  for (const line of lines) {
    const record = parseJsonLine(line);
    if (!record) {
      continue;
    }

    handlers.onRecord?.(record);
    if (record.type === "event") {
      handlers.onEvent?.(record.event);
    }
    if (record.type === "result") {
      finalResult = record.result;
      handlers.onResult?.(record.result);
    }
  }

  return finalResult;
}

export function createStaticEngineRunner({ delayMs = 180, setTimeoutFn = globalThis.setTimeout } = {}) {
  return {
    async generate(project, handlers = {}) {
      const commands = buildProjectCommands(project);
      handlers.onCommand?.(commands.generate);

      const lines = buildSimulatedGenerateOutput(project).split(/\r?\n/);
      let finalResult = null;

      for (const line of lines) {
        await wait(delayMs, setTimeoutFn);
        finalResult = await consumeJsonLines(line, handlers) || finalResult;
      }

      return finalResult;
    },
  };
}
