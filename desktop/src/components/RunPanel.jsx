import { EventList } from "./EventList.jsx";

export function RunPanel({ commands, events, isRunning, isVisible, onClearEvents, onSimulateRun }) {
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
        <button id="simulate-run" className="primary-button" type="button" onClick={onSimulateRun} disabled={isRunning}>
          {isRunning ? "Running..." : "Simulate run"}
        </button>
        <button id="clear-events" className="secondary-button" type="button" onClick={onClearEvents}>
          Clear events
        </button>
      </div>

      <EventList events={events} />
    </section>
  );
}
