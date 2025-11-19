# wordsearch/wordlist_utils.py

"""
Utilidades para cargar, validar y manipular listas de palabras.
Incluye: carga desde txt, slugify y selección de listas (prompt_wordlists).
"""

import os
import re


def load_wordlists_from_txt(path: str):
    """
    Carga listas de palabras desde un .txt.

    Formato esperado:

        palabra1
        palabra2
        palabra3

        palabraA
        palabraB

        palabraX
        ...

    Cada bloque separado por una línea en blanco se interpreta
    como una lista de palabras distinta.

    Devuelve:
        List[List[str]]
    """
    wordlists = []
    current = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Línea en blanco -> separador de listas
            if not line:
                if current:
                    wordlists.append(current)
                    current = []
            else:
                current.append(line)

    # Última lista si el archivo no termina en blanco
    if current:
        wordlists.append(current)

    return wordlists


def slugify(name: str) -> str:
    """
    Convierte un título en un nombre seguro de carpeta/fichero.
    """
    if not name or not isinstance(name, str):
        return "book"
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-]", "", name)
    return name or "book"


def prompt_wordlists(predefined_wordlists):
    """
    Permite elegir el origen de las listas de palabras:
    1) Listas predefinidas del script
    2) Lista manual (una sola lista, separada por comas)
    3) Archivo .txt (una palabra por línea, listas separadas por líneas en blanco)

    Devuelve:
        (wordlists, source_type)
        - wordlists: List[List[str]]
        - source_type: "predefined" | "manual" | "txt"
    """
    print("\n=== Configuración de palabras ===")
    print("1) Usar listas predefinidas (rápido)")
    print("2) Escribir una sola lista manual (se usará en todos los puzzles)")
    print("3) Cargar listas desde un archivo .txt (recomendado: carpeta 'wordlists/')")

    choice = input("Elige opción [1/2/3, por defecto 1]: ").strip() or "1"

    # ----------------------
    # Opción 2: lista manual
    # ----------------------
    if choice == "2":
        raw = input("Escribe las palabras separadas por comas:\n> ")
        words = [w.strip() for w in raw.split(",") if w.strip()]
        if not words:
            print("No se han detectado palabras válidas. Se usarán las listas predefinidas.")
            return predefined_wordlists, "predefined"
        print(f"Se usarán {len(words)} palabras manuales para todos los puzzles.")
        return [words], "manual"

    # ----------------------
    # Opción 3: archivo .txt
    # ----------------------
    if choice == "3":
        base_dir = "wordlists"
        os.makedirs(base_dir, exist_ok=True)

        # Listar .txt disponibles en wordlists/
        txt_files = [f for f in os.listdir(base_dir) if f.lower().endswith(".txt")]
        if txt_files:
            print(f"\nArchivos .txt disponibles en '{base_dir}/':")
            for i, fname in enumerate(txt_files, 1):
                print(f"{i}) {fname}")
            print("Puedes elegir un número de la lista o escribir un nombre/ruta manual.")
        else:
            print(f"\nNo hay archivos .txt en la carpeta '{base_dir}/'.")
            print("Puedes escribir una ruta completa o un nombre que colocarás en esa carpeta.")

        inp = input("Elige número o escribe nombre/ruta del archivo .txt:\n> ").strip()

        # Si pone un número, usamos el índice
        path = inp
        if inp.isdigit() and txt_files:
            idx = int(inp)
            if 1 <= idx <= len(txt_files):
                path = os.path.join(base_dir, txt_files[idx - 1])
        else:
            # Si no es ruta absoluta, asumimos que está en wordlists/
            if not os.path.isabs(path):
                path = os.path.join(base_dir, path)

        try:
            wordlists = load_wordlists_from_txt(path)
            if not wordlists:
                print("No se han encontrado listas válidas en el archivo. Se usarán las listas predefinidas.")
                return predefined_wordlists, "predefined"
            print(f"Se han cargado {len(wordlists)} listas de palabras desde '{path}'.")
            print("Se generará una sopa de letras por cada lista del archivo.")
            return wordlists, "txt"
        except Exception as e:
            print(f"No se pudo leer el archivo: {e}")
            print("Se usarán las listas predefinidas.")
            return predefined_wordlists, "predefined"

    # ----------------------
    # Opción 1 (por defecto)
    # ----------------------
    print("Se usarán las listas predefinidas del script.")
    return predefined_wordlists, "predefined"

def validate_wordlists_for_grid(wordlists, grid_size: int, remove_spaces: bool = True):
    """
    Valida que todas las palabras quepan en un grid de tamaño grid_size.
    Devuelve una lista de problemas encontrados:

        [
            {
                "list_index": índice de la lista (0-based),
                "word": palabra original,
                "clean_word": palabra tras limpieza,
                "length": longitud de clean_word
            },
            ...
        ]

    NO modifica las wordlists. Solo informa.
    """
    problems = []

    for li, wl in enumerate(wordlists):
        for w in wl:
            if not w:
                continue
            w_clean = w.strip()
            if remove_spaces:
                w_clean = w_clean.replace(" ", "")

            if not w_clean:
                continue

            if len(w_clean) > grid_size:
                problems.append({
                    "list_index": li,
                    "word": w,
                    "clean_word": w_clean,
                    "length": len(w_clean),
                })

    return problems

