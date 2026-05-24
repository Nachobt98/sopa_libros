const panels = [
  ["project-panel", "Project"],
  ["content-panel", "Content"],
  ["request-panel", "Request"],
  ["assets-panel", "Assets"],
  ["run-panel", "Run"],
];

export function Sidebar({ activePanel, runtimeLabel, setActivePanel }) {
  return (
    <aside className="sidebar" aria-label="Project navigation">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          SL
        </div>
        <div>
          <h1>sopa-libros</h1>
          <p>KDP word search studio</p>
        </div>
      </div>

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
