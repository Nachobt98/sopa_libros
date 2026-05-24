import { useMemo, useState } from "react";
import { defaultProjectPath, projectToEngineRequest } from "../../app/engineBridge.js";
import { demoProject, normalizeProject } from "../model/project.js";
import { validateProject } from "../model/projectValidation.js";

export function useProjectDocument(initialProject = demoProject) {
  const [project, setProject] = useState(initialProject);
  const [projectPathOverride, setProjectPathOverride] = useState("");
  const [savedProjectJson, setSavedProjectJson] = useState(() => JSON.stringify(normalizeProject(initialProject)));

  const normalizedProject = useMemo(() => normalizeProject(project), [project]);
  const projectJson = useMemo(() => JSON.stringify(normalizedProject, null, 2), [normalizedProject]);
  const request = useMemo(() => projectToEngineRequest(normalizedProject), [normalizedProject]);
  const validation = useMemo(() => validateProject(project), [project]);
  const projectPath = useMemo(
    () => projectPathOverride.trim() || defaultProjectPath(normalizedProject),
    [normalizedProject, projectPathOverride]
  );
  const isDirty = useMemo(() => JSON.stringify(normalizedProject) !== savedProjectJson, [normalizedProject, savedProjectJson]);

  function resetDemoProject() {
    setProject(demoProject);
    setProjectPathOverride("");
    setSavedProjectJson(JSON.stringify(normalizeProject(demoProject)));
  }

  function markSaved(projectOverride = normalizedProject) {
    setSavedProjectJson(JSON.stringify(normalizeProject(projectOverride)));
  }

  function loadProject(projectPayload, path) {
    const loadedProject = normalizeProject(projectPayload);
    setProject(loadedProject);
    setProjectPathOverride(path);
    setSavedProjectJson(JSON.stringify(loadedProject));
  }

  return {
    isDirty,
    loadProject,
    markSaved,
    normalizedProject,
    project,
    projectJson,
    projectPath,
    projectPathOverride,
    request,
    resetDemoProject,
    setProject,
    setProjectPath: setProjectPathOverride,
    validation,
  };
}
