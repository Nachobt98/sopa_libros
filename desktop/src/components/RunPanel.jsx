import { EventList } from "./EventList.jsx";

export function RunPanel({
  commands,
  events,
  isRealEngineAvailable,
  isRunning,
  isVisible,
  lastResult,
  onClearEvents,
  onGenerateProject,
  onValidateProject,
  runningAction,
  validation,
}) {
  const canRun = validation.ok && !isRunning;
  const generateLabel = isRealEngineAvailable ? "Generate PDF" : "Simulate generate";

  return (
    <section id="run-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="run-heading">
      <div className="section-heading">
        <h3 id="run-heading">Run Preview</h3>
        <p>Shows how progress will flow from JSON Lines.</p>
      </div>

      <div className="command-grid">
        <div>
          <h4>Validate</h4>
          <code id="validate-command">{commands.validate}</code>
        </div>
        <div>
          <h4>Generate</h4>
          <code id="generate-command">{commands.generate}</code>
        </div>
      </div>

      <div className="run-toolbar">
        <button id="validate-project" className="secondary-button" type="button" onClick={onValidateProject} disabled={!canRun}>
          {runningAction === "validate" ? "Validating..." : "Validate project"}
        </button>
        <button id="generate-project" className="primary-button" type="button" onClick={onGenerateProject} disabled={!canRun}>
          {runningAction === "generate" ? "Running..." : generateLabel}
        </button>
        <button id="clear-events" className="secondary-button" type="button" onClick={onClearEvents}>
          Clear events
        </button>
      </div>

      {lastResult ? <RunResultSummary result={lastResult} /> : null}
      <EventList events={events} />
    </section>
  );
}

function RunResultSummary({ result }) {
  const issues = result.issues || [];
  return (
    <div className={`run-result ${result.ok ? "is-ok" : "is-error"}`}>
      <div>
        <strong>{result.ok ? "Run completed" : "Run needs attention"}</strong>
        <span>{result.command || "engine command"}</span>
      </div>
      {result.pdf_path ? (
        <div>
          <span>PDF</span>
          <code>{result.pdf_path}</code>
        </div>
      ) : null}
      {issues.length ? (
        <div>
          <span>Issues</span>
          <strong>{issues.length}</strong>
        </div>
      ) : null}
    </div>
  );
}
