export function DocumentStatus({ isDirty, projectPath }) {
  return (
    <div className="document-status" aria-label="Project document status">
      <span id="project-path">{projectPath}</span>
      <span className={`document-state ${isDirty ? "is-dirty" : "is-saved"}`}>{isDirty ? "Sin guardar" : "Guardado"}</span>
    </div>
  );
}
