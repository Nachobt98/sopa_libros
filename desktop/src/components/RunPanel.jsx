import { EventList } from "./EventList.jsx";

export function RunPanel({
  commands,
  events,
  isRealEngineAvailable,
  isRunning,
  isVisible,
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

      <EventList events={events} />
    </section>
  );
}
