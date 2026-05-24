export const demoProject = {
  schema_version: 1,
  project_type: "thematic",
  book_title: "Ancient Egypt Word Search",
  input_path: "wordlists/book_block.txt",
  difficulty: "medium",
  grid_size: 14,
  seed: 1234,
  theme_name: "premium-neutral",
  format_name: "trade-6x9",
  theme_manifest_path: "assets/generated/egypt/asset_manifest.json",
  output_dir: "output_puzzles_kdp/ancient_egypt",
  limit: 5,
  preview: true,
};

export const sampleWords = ["NILE", "PYRAMID", "PHARAOH", "SCARAB", "TEMPLE", "SCRIBE"];
export const sampleLetters = "NILEPYRAMIDPHARAOHSCARABTEMPLESCRIBEANKHOSIRISRAHORUS".repeat(2);

function toNullableString(value) {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
}

function toNullableNumber(value) {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function normalizeProject(project) {
  return {
    ...project,
    book_title: project.book_title.trim() || "Untitled Word Search",
    input_path: project.input_path.trim(),
    grid_size: Number(project.grid_size || 14),
    seed: toNullableNumber(project.seed),
    theme_manifest_path: toNullableString(project.theme_manifest_path),
    output_dir: toNullableString(project.output_dir),
    limit: toNullableNumber(project.limit),
  };
}
