# sopa-libros desktop scaffold

This folder contains the first static UI scaffold for the future desktop app.
It is intentionally dependency-free so the workflow and project contract can be
reviewed before introducing Tauri, React and packaging.

Open locally:

```text
desktop/index.html
```

Current scope:

- edit a thematic `.sopa.json` project draft;
- inspect the engine request generated from that project;
- preview the command lines the future Tauri sidecar will call;
- simulate JSON Lines progress events.

This is not the production desktop app yet. The next step is to replace the
static shell with a Tauri + React implementation that calls:

```text
sopa-libros-engine project validate --project <path>
sopa-libros-engine project generate --project <path> --json-lines
```

