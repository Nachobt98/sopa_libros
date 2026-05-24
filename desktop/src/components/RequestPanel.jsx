export function RequestPanel({ isVisible, normalizedProject, request }) {
  return (
    <section id="request-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="request-heading">
      <div className="section-heading">
        <h3 id="request-heading">Vista técnica</h3>
        <p>Payload que la app enviará a `sopa-libros-engine`.</p>
      </div>
      <div className="split-grid">
        <div>
          <h4>Project JSON</h4>
          <pre id="project-json" className="code-pane">
            {JSON.stringify(normalizedProject, null, 2)}
          </pre>
        </div>
        <div>
          <h4>Request JSON</h4>
          <pre id="request-json" className="code-pane">
            {JSON.stringify(request, null, 2)}
          </pre>
        </div>
      </div>
    </section>
  );
}
