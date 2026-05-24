# sopa-libros desktop app

This folder contains the React/Vite frontend and Tauri shell for the future
desktop app.

Run the frontend in a browser:

```powershell
cd desktop
npm install
npm run vite:dev
```

Current scope:

- edit a thematic `.sopa.json` project draft;
- inspect the engine request generated from that project;
- preview the command lines the future Tauri sidecar will call;
- simulate JSON Lines progress events.

The app-facing engine helpers still live in `desktop/app/engineBridge.js` and
`desktop/app/engineRunner.js` while the UI migrates to React. They have no DOM
dependencies and are covered by Node tests.

The React entry point is `desktop/src/main.jsx`. Vite builds the frontend into
`desktop/dist/`, and Tauri is configured to serve that build.

Run as a Tauri shell after installing the Tauri toolchain and npm dependencies:

```powershell
cd desktop
npm install
npm run dev
```

This is not the production desktop app yet. The next step is to replace the
static runner with a Tauri-backed implementation that calls:

```text
sopa-libros-engine project validate --project <path>
sopa-libros-engine project generate --project <path> --json-lines
```

