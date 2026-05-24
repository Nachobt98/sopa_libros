# sopa-libros desktop scaffold

This folder contains the first static UI scaffold for the future desktop app.
It is intentionally dependency-free so the workflow and project contract can be
reviewed before introducing Tauri, React and packaging.

Open locally without Tauri:

```text
desktop/index.html
```

Current scope:

- edit a thematic `.sopa.json` project draft;
- inspect the engine request generated from that project;
- preview the command lines the future Tauri sidecar will call;
- simulate JSON Lines progress events.

The sidecar-facing browser logic lives in `engineBridge.js`. It has no DOM
dependencies, so it can move into a React/Tauri adapter later with minimal
rewrite.

The static app assets live in `desktop/app/`. The root `desktop/index.html`
redirects there so older local links continue to work.

Run as a Tauri shell after installing the Tauri toolchain and npm dependencies:

```powershell
cd desktop
npm install
npm run dev
```

This is not the production desktop app yet. The next step is to replace the
static shell with a React implementation that calls:

```text
sopa-libros-engine project validate --project <path>
sopa-libros-engine project generate --project <path> --json-lines
```

