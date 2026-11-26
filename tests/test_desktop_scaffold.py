from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"
DESKTOP_APP = DESKTOP / "app"


def test_desktop_scaffold_files_exist():
    assert (DESKTOP / "index.html").exists()
    assert (DESKTOP / "vite.config.js").exists()
    assert (DESKTOP / "src" / "main.jsx").exists()
    assert (DESKTOP / "src" / "App.jsx").exists()
    assert (DESKTOP / "src" / "components" / "ProjectForm.jsx").exists()
    assert (DESKTOP / "src" / "components" / "DocumentStatus.jsx").exists()
    assert (DESKTOP / "src" / "components" / "RunPanel.jsx").exists()
    assert (DESKTOP / "src" / "components" / "ValidationSummary.jsx").exists()
    assert (DESKTOP / "src" / "hooks" / "useEngineRuntime.js").exists()
    assert (DESKTOP / "src" / "hooks" / "useProjectDocument.js").exists()
    assert (DESKTOP / "src" / "hooks" / "useProjectDocument.test.mjs").exists()
    assert (DESKTOP / "src" / "hooks" / "useProjectFileActions.js").exists()
    assert (DESKTOP / "src" / "hooks" / "useProjectRun.js").exists()
    assert (DESKTOP / "src" / "model" / "project.js").exists()
    assert (DESKTOP / "src" / "model" / "projectValidation.js").exists()
    assert (DESKTOP / "src" / "model" / "projectValidation.test.mjs").exists()
    assert (DESKTOP_APP / "index.html").exists()
    assert (DESKTOP_APP / "styles.css").exists()
    assert (DESKTOP_APP / "app.js").exists()
    assert (DESKTOP_APP / "engineBridge.js").exists()
    assert (DESKTOP_APP / "engineBridge.test.mjs").exists()
    assert (DESKTOP_APP / "engineRunner.js").exists()
    assert (DESKTOP_APP / "engineRunner.test.mjs").exists()
    assert (DESKTOP_APP / "tauriEngineBridge.js").exists()
    assert (DESKTOP_APP / "tauriEngineBridge.test.mjs").exists()
    assert (DESKTOP_APP / "projectFileBridge.js").exists()
    assert (DESKTOP_APP / "projectFileBridge.test.mjs").exists()
    assert (DESKTOP / "README.md").exists()
    assert (DESKTOP / "package.json").exists()
    assert (DESKTOP / "src-tauri" / "tauri.conf.json").exists()
    assert (DESKTOP / "src-tauri" / "icons" / "icon.ico").exists()


def test_desktop_index_references_local_assets():
    html = (DESKTOP / "index.html").read_text(encoding="utf-8")
    legacy_html = (DESKTOP_APP / "index.html").read_text(encoding="utf-8")
    project_form = (DESKTOP / "src" / "components" / "ProjectForm.jsx").read_text(encoding="utf-8")
    request_panel = (DESKTOP / "src" / "components" / "RequestPanel.jsx").read_text(encoding="utf-8")
    event_list = (DESKTOP / "src" / "components" / "EventList.jsx").read_text(encoding="utf-8")
    validation_summary = (DESKTOP / "src" / "components" / "ValidationSummary.jsx").read_text(encoding="utf-8")
    document_status = (DESKTOP / "src" / "components" / "DocumentStatus.jsx").read_text(encoding="utf-8")

    assert '<div id="root"></div>' in html
    assert '<script type="module" src="/src/main.jsx"></script>' in html
    assert '<script type="module" src="./app.js"></script>' in legacy_html
    assert 'id="project-form"' in project_form
    assert 'value="christmas-vintage"' in project_form
    assert 'value="christmas-vintage"' in legacy_html
    assert 'id="request-json"' in request_panel
    assert 'id="event-list"' in event_list
    assert 'id="validation-summary"' in validation_summary
    assert 'id="project-path"' in document_status


def test_desktop_app_mentions_engine_project_commands():
    app = (DESKTOP / "src" / "App.jsx").read_text(encoding="utf-8")
    sidebar = (DESKTOP / "src" / "components" / "Sidebar.jsx").read_text(encoding="utf-8")
    bridge = (DESKTOP_APP / "engineBridge.js").read_text(encoding="utf-8")
    runner = (DESKTOP_APP / "engineRunner.js").read_text(encoding="utf-8")
    tauri_bridge = (DESKTOP_APP / "tauriEngineBridge.js").read_text(encoding="utf-8")
    file_bridge = (DESKTOP_APP / "projectFileBridge.js").read_text(encoding="utf-8")

    assert "sopa-libros-engine project validate" in bridge
    assert "sopa-libros-engine project generate" in bridge
    assert "--json-lines" in bridge
    assert "createStaticEngineRunner" in runner
    assert "consumeJsonLines" in runner
    assert "engine_runtime_status" in tauri_bridge
    assert "run_engine_project_command" in tauri_bridge
    assert "save_project_file" in file_bridge
    assert "read_project_file" in file_bridge
    assert "Copy project JSON" in app
    assert "Save draft" in app
    assert "generateProject" in app
    assert "validateProject" in app
    assert "runtimeLabel" in sidebar


def test_tauri_config_points_to_static_app_directory():
    config = (DESKTOP / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")

    assert '"beforeDevCommand": "npm run vite:dev"' in config
    assert '"beforeBuildCommand": "npm run build"' in config
    assert '"devUrl": "http://127.0.0.1:5173"' in config
    assert '"frontendDist": "../dist"' in config
    assert '"withGlobalTauri": true' in config
    assert '"icon": ["icons/icon.ico"]' in config
    assert '"identifier": "com.sopalibros.desktop"' in config


def test_tauri_registers_engine_commands():
    lib = (DESKTOP / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")

    assert "#[tauri::command]" in lib
    assert "engine_runtime_status" in lib
    assert "run_engine_project_command" in lib
    assert "save_project_file" in lib
    assert "read_project_file" in lib
    assert "tauri::generate_handler!" in lib
