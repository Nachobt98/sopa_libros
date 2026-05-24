export function DashboardPanel({
  contentState,
  fileActions,
  isVisible,
  onCopyProject,
  onNavigate,
  project,
  projectDocument,
  recentProjects,
  runState,
  validation,
}) {
  const hasManifest = Boolean(project.theme_manifest_path);
  const hasContent = Boolean(contentState.loadedPath || contentState.content.trim() || project.input_path);
  const lastRunLabel = runState.lastResult?.pdf_path || (runState.lastResult ? "Revisar incidencias" : "Pendiente");

  return (
    <section id="home-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="home-heading">
      <div className="home-layout">
        <div className="home-main">
          <div className="welcome-block">
            <p className="eyebrow">PuzzleForge Studio</p>
            <h3 id="home-heading">Crea, revisa y exporta tu libro de sopas de letras</h3>
            <p>Organiza el contenido, prepara los assets visuales y lanza la generación desde un flujo único.</p>
          </div>

          <div className="action-grid">
            <ActionCard
              icon="+"
              title="Nuevo proyecto"
              text="Vuelve al proyecto base y empieza una nueva configuración."
              button="Crear proyecto"
              onClick={projectDocument.resetDemoProject}
              tone="violet"
            />
            <ActionCard
              icon="Aa"
              title="Contenido"
              text="Edita el TXT temático que alimenta puzzles, bloques y facts."
              button="Editar contenido"
              onClick={() => onNavigate("content-panel")}
              tone="green"
            />
            <ActionCard
              icon="□"
              title="Assets"
              text="Convierte imágenes revisadas en un manifest listo para render."
              button="Preparar assets"
              onClick={() => onNavigate("assets-panel")}
              tone="amber"
            />
            <ActionCard
              icon="✓"
              title="Validación y PDF"
              text="Valida el proyecto y genera el PDF final con el engine."
              button="Ir a ejecutar"
              onClick={() => onNavigate("run-panel")}
              tone="blue"
            />
          </div>

          <div className="studio-section">
            <div className="section-title-row">
              <h4>Proyecto actual</h4>
              <button className="link-button" type="button" onClick={() => onNavigate("project-panel")}>
                Editar
              </button>
            </div>
            <div className="current-project-card">
              <div>
                <strong>{project.book_title}</strong>
                <span>{project.input_path}</span>
              </div>
              <div className="project-badges">
                <span>{project.format_name}</span>
                <span>{project.difficulty}</span>
                {project.preview ? <span>preview</span> : null}
              </div>
            </div>
          </div>

          <div className="studio-section">
            <div className="section-title-row">
              <h4>Proyectos recientes</h4>
              <span>{recentProjects.length ? `${recentProjects.length} guardados` : "Sin historial"}</span>
            </div>
            {recentProjects.length ? (
              <div className="recent-projects">
                {recentProjects.map((item) => (
                  <button key={item.path} type="button" onClick={() => projectDocument.setProjectPath(item.path)}>
                    <strong>{item.title}</strong>
                    <span>{item.path}</span>
                  </button>
                ))}
              </div>
            ) : (
              <p className="empty-note">Guarda o abre un proyecto para que aparezca aqui.</p>
            )}
          </div>

          <div className="quick-actions">
            <button type="button" onClick={fileActions.openProject} disabled={!fileActions.canLoad || fileActions.isLoading}>
              Abrir proyecto
            </button>
            <button type="button" onClick={fileActions.saveDraft} disabled={!fileActions.canSave || fileActions.isSaving}>
              Guardar proyecto
            </button>
            <button type="button" onClick={onCopyProject}>
              Copiar JSON
            </button>
            <button type="button" onClick={() => onNavigate("request-panel")}>
              Ver técnico
            </button>
          </div>
        </div>

        <aside className="home-side" aria-label="Resumen del proyecto">
          <div className="status-card">
            <h4>Estado rápido</h4>
            <StatusRow label="Proyecto" value={projectDocument.isDirty ? "Cambios sin guardar" : "Guardado"} ok={!projectDocument.isDirty} />
            <StatusRow label="Contenido" value={contentState.loadedPath ? "TXT cargado" : hasContent ? "Ruta definida" : "Pendiente"} ok={hasContent} />
            <StatusRow label="Assets" value={hasManifest ? "Manifest asignado" : "Sin manifest"} ok={hasManifest} />
            <StatusRow label="Validación" value={validation.ok ? "Lista" : `${validation.issues.length} incidencias`} ok={validation.ok} />
            <StatusRow label="Último PDF" value={lastRunLabel} ok={Boolean(runState.lastResult?.ok)} />
          </div>

          <div className="tip-card">
            <h4>Siguiente paso</h4>
            <p>{nextStepText({ hasManifest, validation, contentState, runState })}</p>
          </div>
        </aside>
      </div>
    </section>
  );
}

function ActionCard({ button, icon, onClick, text, title, tone }) {
  return (
    <article className={`action-card tone-${tone}`}>
      <div className="action-icon" aria-hidden="true">
        {icon}
      </div>
      <h4>{title}</h4>
      <p>{text}</p>
      <button type="button" onClick={onClick}>
        {button}
      </button>
    </article>
  );
}

function StatusRow({ label, ok, value }) {
  return (
    <div className="status-row">
      <span className={ok ? "status-marker is-ok" : "status-marker"}></span>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function nextStepText({ contentState, hasManifest, runState, validation }) {
  if (!validation.ok) {
    return "Revisa los ajustes del proyecto antes de validar o generar.";
  }
  if (!contentState.loadedPath && !contentState.content.trim()) {
    return "Carga, guarda o crea una plantilla TXT para trabajar con contenido real desde la app.";
  }
  if (!hasManifest) {
    return "Prepara un manifest de assets o deja el render con fondos por defecto.";
  }
  if (!runState.lastResult) {
    return "Ejecuta la validación y genera un PDF de prueba.";
  }
  return runState.lastResult.ok ? "Ya hay una generación correcta. Revisa el PDF y ajusta la experiencia visual." : "La última ejecución dejó incidencias; abre Run para revisarlas.";
}
