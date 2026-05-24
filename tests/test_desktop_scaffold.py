from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"
DESKTOP_APP = DESKTOP / "app"


def test_desktop_scaffold_files_exist():
    assert (DESKTOP / "index.html").exists()
    assert (DESKTOP / "vite.config.js").exists()
    assert (DESKTOP / "src" / "main.jsx").exists()
    assert (DESKTOP / "src" / "App.jsx").exists()
    assert (DESKTOP_APP / "index.html").exists()
    assert (DESKTOP_APP / "styles.css").exists()
    assert (DESKTOP_APP / "app.js").exists()
    assert (DESKTOP_APP / "engineBridge.js").exists()
    assert (DESKTOP_APP / "engineBridge.test.mjs").exists()
    assert (DESKTOP_APP / "engineRunner.js").exists()
    assert (DESKTOP_APP / "engineRunner.test.mjs").exists()
    assert (DESKTOP / "README.md").exists()
    assert (DESKTOP / "package.json").exists()
    assert (DESKTOP / "src-tauri" / "tauri.conf.json").exists()


def test_desktop_index_references_local_assets():
    html = (DESKTOP / "index.html").read_text(encoding="utf-8")
    legacy_html = (DESKTOP_APP / "index.html").read_text(encoding="utf-8")
    app = (DESKTOP / "src" / "App.jsx").read_text(encoding="utf-8")

    assert '<div id="root"></div>' in html
    assert '<script type="module" src="/src/main.jsx"></script>' in html
    assert '<script type="module" src="./app.js"></script>' in legacy_html
    assert 'id="project-form"' in app
    assert 'id="request-json"' in app
    assert 'id="event-list"' in app


def test_desktop_app_mentions_engine_project_commands():
    app = (DESKTOP / "src" / "App.jsx").read_text(encoding="utf-8")
    bridge = (DESKTOP_APP / "engineBridge.js").read_text(encoding="utf-8")
    runner = (DESKTOP_APP / "engineRunner.js").read_text(encoding="utf-8")

    assert "sopa-libros-engine project validate" in bridge
    assert "sopa-libros-engine project generate" in bridge
    assert "--json-lines" in bridge
    assert "createStaticEngineRunner" in runner
    assert "consumeJsonLines" in runner
    assert "Copy project JSON" in app
    assert "React scaffold" in app


def test_tauri_config_points_to_static_app_directory():
    config = (DESKTOP / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")

    assert '"beforeDevCommand": "npm run vite:dev"' in config
    assert '"beforeBuildCommand": "npm run build"' in config
    assert '"devUrl": "http://127.0.0.1:5173"' in config
    assert '"frontendDist": "../dist"' in config
    assert '"identifier": "com.sopalibros.desktop"' in config
