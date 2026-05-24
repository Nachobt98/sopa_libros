import { useEffect, useState } from "react";

const STORAGE_KEY = "sopaLibros.recentProjects";

function readRecentProjects(storage = window.localStorage) {
  try {
    const parsed = JSON.parse(storage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.slice(0, 6) : [];
  } catch {
    return [];
  }
}

function writeRecentProjects(projects, storage = window.localStorage) {
  storage.setItem(STORAGE_KEY, JSON.stringify(projects.slice(0, 6)));
}

export function useRecentProjects() {
  const [recentProjects, setRecentProjects] = useState(() => readRecentProjects());

  useEffect(() => {
    writeRecentProjects(recentProjects);
  }, [recentProjects]);

  function rememberProject(project, path) {
    if (!path) {
      return;
    }
    setRecentProjects((current) => {
      const withoutDuplicate = current.filter((item) => item.path !== path);
      return [
        {
          title: project.book_title || "Proyecto sin titulo",
          path,
          inputPath: project.input_path || "",
          updatedAt: new Date().toISOString(),
        },
        ...withoutDuplicate,
      ].slice(0, 6);
    });
  }

  return {
    recentProjects,
    rememberProject,
  };
}
