const allowedDifficulties = new Set(["easy", "medium", "hard"]);

export function validateProject(project) {
  const issues = [];

  if (!project.book_title.trim()) {
    issues.push({ field: "book_title", message: "Book title is required." });
  }

  if (!project.input_path.trim()) {
    issues.push({ field: "input_path", message: "Thematic TXT input is required." });
  }

  if (!allowedDifficulties.has(project.difficulty)) {
    issues.push({ field: "difficulty", message: "Difficulty must be easy, medium, or hard." });
  }

  const gridSize = Number(project.grid_size);
  if (!Number.isInteger(gridSize) || gridSize < 6 || gridSize > 30) {
    issues.push({ field: "grid_size", message: "Grid size must be an integer between 6 and 30." });
  }

  if (project.limit !== null && project.limit !== undefined && project.limit !== "") {
    const limit = Number(project.limit);
    if (!Number.isInteger(limit) || limit < 1) {
      issues.push({ field: "limit", message: "Puzzle limit must be a positive integer." });
    }
  }

  return {
    ok: issues.length === 0,
    issues,
  };
}
