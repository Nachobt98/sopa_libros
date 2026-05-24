import { ProjectForm } from "./ProjectForm.jsx";
import { ValidationSummary } from "./ValidationSummary.jsx";

export function ProjectPanel({ isVisible, project, setProject, validation }) {
  return (
    <section id="project-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="project-heading">
      <div className="section-heading">
        <h3 id="project-heading">Project Settings</h3>
        <p>These fields map to the `.sopa.json` project model.</p>
      </div>
      <ValidationSummary validation={validation} />
      <ProjectForm project={project} setProject={setProject} />
    </section>
  );
}
