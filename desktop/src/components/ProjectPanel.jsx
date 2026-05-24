import { ProjectForm } from "./ProjectForm.jsx";

export function ProjectPanel({ isVisible, project, setProject }) {
  return (
    <section id="project-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="project-heading">
      <div className="section-heading">
        <h3 id="project-heading">Project Settings</h3>
        <p>These fields map to the `.sopa.json` project model.</p>
      </div>
      <ProjectForm project={project} setProject={setProject} />
    </section>
  );
}
