import { useMemo, useState } from "react";

export function AssetsPanel({
  assetResult,
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
          <p>Prepare reviewed images for the renderer manifest.</p>
        </div>
      </div>

      <div className="asset-status">
        <strong>Current manifest</strong>
        <code>{manifestPath}</code>
      </div>

      <form className="asset-form" onSubmit={submit}>
        <label>
          <span>User assets folder</span>
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
          <span>Output folder</span>
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
          <span>Style label</span>
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
            {isBuildingAssets ? "Building manifest..." : "Build asset manifest"}
          </button>
          {!isRealEngineAvailable ? <span>Desktop runtime required.</span> : null}
        </div>
      </form>

      {assetResult?.assets ? (
        <div className="asset-result">
          <div>
            <span>Manifest</span>
            <code>{assetResult.assets.manifest_path}</code>
          </div>
          <div>
            <span>Source map</span>
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
