const panels = [
  ["home-panel", "Inicio"],
  ["project-panel", "Proyecto"],
  ["content-panel", "Contenido"],
  ["assets-panel", "Assets"],
  ["run-panel", "Validar y exportar"],
  ["request-panel", "Técnico"],
];

export function Sidebar({ activePanel, runtimeLabel, setActivePanel }) {
  return (
    <aside className="sidebar" aria-label="Project navigation">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          PF
        </div>
        <div>
          <h1>PuzzleForge Studio</h1>
          <p>Crea. Diseña. Publica.</p>
        </div>
      </div>

      <button className="new-project-button" type="button" onClick={() => setActivePanel("project-panel")}>
        <span aria-hidden="true">+</span>
        Nuevo proyecto
      </button>

      <nav className="nav-stack" aria-label="Workflow">
        {panels.map(([panel, label]) => (
          <button
            key={panel}
            className={`nav-item ${activePanel === panel ? "is-active" : ""}`}
            type="button"
            onClick={() => setActivePanel(panel)}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="status-block">
        <span className="status-dot"></span>
        <span>{runtimeLabel}</span>
      </div>
    </aside>
  );
}
