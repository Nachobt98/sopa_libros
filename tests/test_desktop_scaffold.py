from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"


def test_desktop_scaffold_files_exist():
    assert (DESKTOP / "index.html").exists()
    assert (DESKTOP / "styles.css").exists()
    assert (DESKTOP / "app.js").exists()
    assert (DESKTOP / "README.md").exists()


def test_desktop_index_references_local_assets():
    html = (DESKTOP / "index.html").read_text(encoding="utf-8")

    assert '<link rel="stylesheet" href="./styles.css" />' in html
    assert '<script src="./app.js"></script>' in html
    assert 'id="project-form"' in html
    assert 'id="request-json"' in html
    assert 'id="event-list"' in html


def test_desktop_app_mentions_engine_project_commands():
    html = (DESKTOP / "index.html").read_text(encoding="utf-8")
    script = (DESKTOP / "app.js").read_text(encoding="utf-8")

    assert "sopa-libros-engine project validate" in script
    assert "sopa-libros-engine project generate" in script
    assert "--json-lines" in script
    assert "Copy project JSON" in html
