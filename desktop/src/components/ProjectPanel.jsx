import { ProjectForm } from "./ProjectForm.jsx";
import { ValidationSummary } from "./ValidationSummary.jsx";

export function ProjectPanel({ isVisible, project, setProject, validation }) {
  return (
    <section id="project-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="project-heading">
      <div className="section-heading">
        <h3 id="project-heading">Configuración del proyecto</h3>
        <p>Ajustes principales del libro y del PDF.</p>
      </div>
      <ValidationSummary validation={validation} />
      <ProjectForm project={project} setProject={setProject} />
    </section>
  );
}
