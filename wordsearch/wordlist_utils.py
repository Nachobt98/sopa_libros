"""
Utilidades para cargar, validar y manipular listas de palabras.
Incluye: carga desde txt, validación, limpieza, etc.
"""

def load_wordlists_from_txt(path: str):
    # ...
    pass

def slugify(name: str) -> str:
    import re
    if not name or not isinstance(name, str):
        return "book"
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-]", "", name)
    return name or "book"
