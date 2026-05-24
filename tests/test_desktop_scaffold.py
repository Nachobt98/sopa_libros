from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"
DESKTOP_APP = DESKTOP / "app"


def test_desktop_scaffold_files_exist():
    assert (DESKTOP / "index.html").exists()
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
    html = (DESKTOP_APP / "index.html").read_text(encoding="utf-8")

    assert '<link rel="stylesheet" href="./styles.css" />' in html
    assert '<script type="module" src="./app.js"></script>' in html
    assert 'id="project-form"' in html
    assert 'id="request-json"' in html
    assert 'id="event-list"' in html


def test_desktop_app_mentions_engine_project_commands():
    html = (DESKTOP_APP / "index.html").read_text(encoding="utf-8")
    bridge = (DESKTOP_APP / "engineBridge.js").read_text(encoding="utf-8")
    runner = (DESKTOP_APP / "engineRunner.js").read_text(encoding="utf-8")

    assert "sopa-libros-engine project validate" in bridge
    assert "sopa-libros-engine project generate" in bridge
    assert "--json-lines" in bridge
    assert "createStaticEngineRunner" in runner
    assert "consumeJsonLines" in runner
    assert "Copy project JSON" in html


def test_tauri_config_points_to_static_app_directory():
    config = (DESKTOP / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")

    assert '"frontendDist": "../app"' in config
    assert '"identifier": "com.sopalibros.desktop"' in config
