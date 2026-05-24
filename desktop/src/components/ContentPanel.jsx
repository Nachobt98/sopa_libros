export function ContentPanel({
  contentState,
  inputPath,
  isVisible,
}) {
  const canLoad = contentState.canUseFiles && !contentState.isLoadingContent && inputPath.trim();
  const canSave = contentState.canUseFiles && !contentState.isSavingContent && inputPath.trim();
  const loadedLabel = contentState.loadedPath || "No content loaded";

  return (
    <section id="content-panel" className={`panel ${isVisible ? "is-visible" : ""}`} aria-labelledby="content-heading">
      <div className="section-heading">
        <div>
          <h3 id="content-heading">Content</h3>
          <p>Edit the thematic TXT used by validation and generation.</p>
        </div>
        <div className="content-actions">
          <button
            id="load-content"
            className="secondary-button"
            type="button"
            onClick={() => contentState.loadContent(inputPath)}
            disabled={!canLoad}
          >
            {contentState.isLoadingContent ? "Loading..." : "Load TXT"}
          </button>
          <button
            id="save-content"
            className="primary-button"
            type="button"
            onClick={() => contentState.saveContent(inputPath)}
            disabled={!canSave}
          >
            {contentState.isSavingContent ? "Saving..." : "Save TXT"}
          </button>
        </div>
      </div>

      <div className="content-status">
        <span>{contentState.isDirty ? "Unsaved content" : "Content saved"}</span>
        <code>{loadedLabel}</code>
      </div>

      <textarea
        id="content-editor"
        className="content-editor"
        value={contentState.content}
        onChange={(event) => contentState.setContent(event.target.value)}
        spellCheck="false"
      />
    </section>
  );
}
