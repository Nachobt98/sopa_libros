import { useMemo, useState } from "react";
import { defaultProjectPath, projectToEngineRequest } from "../../app/engineBridge.js";
import { demoProject, normalizeProject } from "../model/project.js";
import { validateProject } from "../model/projectValidation.js";

export function useProjectDocument(initialProject = demoProject) {
  const [project, setProject] = useState(initialProject);
  const [savedProjectJson, setSavedProjectJson] = useState(() => JSON.stringify(normalizeProject(initialProject)));

  const normalizedProject = useMemo(() => normalizeProject(project), [project]);
  const projectJson = useMemo(() => JSON.stringify(normalizedProject, null, 2), [normalizedProject]);
  const request = useMemo(() => projectToEngineRequest(normalizedProject), [normalizedProject]);
  const validation = useMemo(() => validateProject(project), [project]);
  const projectPath = useMemo(() => defaultProjectPath(normalizedProject), [normalizedProject]);
  const isDirty = useMemo(() => JSON.stringify(normalizedProject) !== savedProjectJson, [normalizedProject, savedProjectJson]);

  function resetDemoProject() {
    setProject(demoProject);
    setSavedProjectJson(JSON.stringify(normalizeProject(demoProject)));
  }

  function markSaved() {
    setSavedProjectJson(JSON.stringify(normalizedProject));
  }

  return {
    isDirty,
    markSaved,
    normalizedProject,
    project,
    projectJson,
    projectPath,
    request,
    resetDemoProject,
    setProject,
    validation,
  };
}
