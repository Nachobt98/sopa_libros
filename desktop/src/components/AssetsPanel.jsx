import { useMemo, useState } from "react";

import { analyzeThematicContent } from "../model/contentAnalysis.js";

export function AssetsPanel({
  assetResult,
  content,
  isBuildingAssets,
  isRealEngineAvailable,
  isVisible,
  onBuildUserAssets,
  project,
  validation,
}) {
  const [userAssetsDir, setUserAssetsDir] = useState("assets/user");
  const [outputDir, setOutputDir] = useState("");
  const [style, setStyle] = useState("reviewed-user-assets");
  const canBuild = validation.ok && !isBuildingAssets && isRealEngineAvailable && userAssetsDir.trim();
  const manifestPath = project.theme_manifest_path || "No manifest selected";
  const contentAnalysis = analyzeThematicContent(content);
  const expectedBlocks = contentAnalysis.blocks.length ? contentAnalysis.blocks : [{ name: "Default", slug: "default" }];
  const outputPlaceholder = useMemo(() => {
    const slug = project.book_title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "");
    return `assets/generated/${slug || "book"}-user`;
  }, [project.book_title]);

  function submit(event) {
    event.preventDefault();
    onBuildUserAssets({
      userAssetsDir: userAssetsDir.trim(),
      outputDir: outputDir.trim() || null,
      style: style.trim() || "reviewed-user-assets",
    });
  }

  return (
    <section id="assets-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="assets-heading">
      <div className="section-heading">
        <div>
          <h3 id="assets-heading">Assets</h3>
          <p>Prepara imágenes revisadas para el manifest del render.</p>
        </div>
      </div>

      <div className="asset-status">
        <strong>Manifest actual</strong>
        <code>{manifestPath === "No manifest selected" ? "Sin manifest seleccionado" : manifestPath}</code>
      </div>

      <form className="asset-form" onSubmit={submit}>
        <label>
          <span>Carpeta de imágenes</span>
          <input
            id="user-assets-dir"
            name="userAssetsDir"
            type="text"
            autoComplete="off"
            value={userAssetsDir}
            onChange={(event) => setUserAssetsDir(event.target.value)}
          />
        </label>

        <label>
          <span>Carpeta de salida</span>
          <input
            id="asset-output-dir"
            name="assetOutputDir"
            type="text"
            autoComplete="off"
            placeholder={outputPlaceholder}
            value={outputDir}
            onChange={(event) => setOutputDir(event.target.value)}
          />
        </label>

        <label>
          <span>Etiqueta de estilo</span>
          <input
            id="asset-style"
            name="assetStyle"
            type="text"
            autoComplete="off"
            value={style}
            onChange={(event) => setStyle(event.target.value)}
          />
        </label>

        <div className="asset-actions">
          <button id="build-user-assets" className="primary-button" type="submit" disabled={!canBuild}>
            {isBuildingAssets ? "Construyendo manifest..." : "Crear manifest"}
          </button>
          {!isRealEngineAvailable ? <span>Requiere runtime desktop.</span> : null}
        </div>
      </form>

      <div className="asset-checklist">
        <div className="section-title-row">
          <h4>Nombres esperados</h4>
          <span>{expectedBlocks.length} bloque{expectedBlocks.length === 1 ? "" : "s"}</span>
        </div>
        <div className="asset-name-grid">
          <div>
            <strong>Fondo global</strong>
            <code>default_background.png</code>
            <code>book_default_background.jpg</code>
          </div>
          {expectedBlocks.map((block, index) => (
            <div key={block.slug}>
              <strong>{block.name}</strong>
              <code>block_{String(index + 1).padStart(2, "0")}_{block.slug}_background.png</code>
              <code>{block.slug}_cover.png</code>
            </div>
          ))}
        </div>
      </div>

      {assetResult?.assets ? (
        <div className="asset-result">
          <div>
            <span>Manifest</span>
            <code>{assetResult.assets.manifest_path}</code>
          </div>
          <div>
            <span>Mapa de fuentes</span>
            <code>{assetResult.assets.source_map_path}</code>
          </div>
          <div className="asset-metrics">
            <strong>{assetResult.assets.asset_count}</strong>
            <span>assets</span>
            <strong>{assetResult.assets.block_count}</strong>
            <span>blocks</span>
            <strong>{assetResult.assets.warning_count}</strong>
            <span>warnings</span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
