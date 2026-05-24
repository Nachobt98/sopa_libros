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
  onOpenPath,
  onValidateProject,
  runningAction,
  validation,
}) {
  const canRun = validation.ok && !isRunning;
  const generateLabel = isRealEngineAvailable ? "Generar PDF" : "Simular generación";

  return (
    <section id="run-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="run-heading">
      <div className="section-heading">
        <h3 id="run-heading">Validar y exportar</h3>
        <p>Ejecuta el engine real y revisa el resultado.</p>
      </div>

      <div className="run-step-grid">
        <RunStep label="Contenido" state="ready" />
        <RunStep label="Assets" state="ready" />
        <RunStep label="Validacion" state={lastResult && !lastResult.ok ? "warning" : "ready"} />
        <RunStep label="PDF" state={lastResult?.pdf_path ? "ready" : "pending"} />
      </div>

      <details className="command-details">
        <summary>Ver comandos</summary>
        <div className="command-grid">
          <div>
            <h4>Validar</h4>
            <code id="validate-command">{commands.validate}</code>
          </div>
          <div>
            <h4>Generar</h4>
            <code id="generate-command">{commands.generate}</code>
          </div>
        </div>
      </details>

      <div className="run-toolbar">
        <button id="validate-project" className="secondary-button" type="button" onClick={onValidateProject} disabled={!canRun}>
          {runningAction === "validate" ? "Validando..." : "Validar proyecto"}
        </button>
        <button id="generate-project" className="primary-button" type="button" onClick={onGenerateProject} disabled={!canRun}>
          {runningAction === "generate" ? "Ejecutando..." : generateLabel}
        </button>
        <button id="clear-events" className="secondary-button" type="button" onClick={onClearEvents}>
          Limpiar eventos
        </button>
      </div>

      {lastResult ? <RunResultSummary result={lastResult} /> : null}
      {lastResult?.pdf_path ? (
        <div className="run-output-actions">
          <button className="primary-button" type="button" onClick={() => onOpenPath(lastResult.pdf_path)}>
            Abrir PDF
          </button>
          <button className="secondary-button" type="button" onClick={() => onOpenPath(lastResult.pdf_path.replace(/[\\/][^\\/]+$/, ""))}>
            Abrir carpeta
          </button>
        </div>
      ) : null}
      <EventList events={events} />
    </section>
  );
}

function RunStep({ label, state }) {
  return (
    <div className={`run-step is-${state}`}>
      <span></span>
      <strong>{label}</strong>
    </div>
  );
}

function RunResultSummary({ result }) {
  const issues = result.issues || [];
  return (
    <div className={`run-result ${result.ok ? "is-ok" : "is-error"}`}>
      <div>
        <strong>{result.ok ? "Ejecución completada" : "Revisar ejecución"}</strong>
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
          <span>Incidencias</span>
          <strong>{issues.length}</strong>
        </div>
      ) : null}
    </div>
  );
}
