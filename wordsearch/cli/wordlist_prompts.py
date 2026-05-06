"""Interactive prompts for selecting simple word lists."""

from __future__ import annotations

import os

from wordsearch.io.wordlists import load_wordlists_from_txt


def prompt_wordlists(predefined_wordlists: list[list[str]]) -> tuple[list[list[str]], str]:
    """
    Prompt for the source of simple word lists.

    Returns ``(wordlists, source_type)`` where source type is one of
    ``predefined``, ``manual`` or ``txt``.
    """
    print("\n=== Configuracion de palabras ===")
    print("1) Usar listas predefinidas (rapido)")
    print("2) Escribir una sola lista manual (se usara en todos los puzzles)")
    print("3) Cargar listas desde un archivo .txt (recomendado: carpeta 'wordlists/')")

    choice = input("Elige opcion [1/2/3, por defecto 1]: ").strip() or "1"

    if choice == "2":
        raw = input("Escribe las palabras separadas por comas:\n> ")
        words = [word.strip() for word in raw.split(",") if word.strip()]
        if not words:
            print("No se han detectado palabras validas. Se usaran las listas predefinidas.")
            return predefined_wordlists, "predefined"
        print(f"Se usaran {len(words)} palabras manuales para todos los puzzles.")
        return [words], "manual"

    if choice == "3":
        base_dir = "wordlists"
        os.makedirs(base_dir, exist_ok=True)

        txt_files = [fname for fname in os.listdir(base_dir) if fname.lower().endswith(".txt")]
        if txt_files:
            print(f"\nArchivos .txt disponibles en '{base_dir}/':")
            for index, filename in enumerate(txt_files, 1):
                print(f"{index}) {filename}")
            print("Puedes elegir un numero de la lista o escribir un nombre/ruta manual.")
        else:
            print(f"\nNo hay archivos .txt en la carpeta '{base_dir}/'.")
            print("Puedes escribir una ruta completa o un nombre que colocaras en esa carpeta.")

        user_input = input("Elige numero o escribe nombre/ruta del archivo .txt:\n> ").strip()

        path = user_input
        if user_input.isdigit() and txt_files:
            index = int(user_input)
            if 1 <= index <= len(txt_files):
                path = os.path.join(base_dir, txt_files[index - 1])
        elif not os.path.isabs(path):
            path = os.path.join(base_dir, path)

        try:
            wordlists = load_wordlists_from_txt(path)
            if not wordlists:
                print("No se han encontrado listas validas en el archivo. Se usaran las listas predefinidas.")
                return predefined_wordlists, "predefined"
            print(f"Se han cargado {len(wordlists)} listas de palabras desde '{path}'.")
            print("Se generara una sopa de letras por cada lista del archivo.")
            return wordlists, "txt"
        except Exception as exc:
            print(f"No se pudo leer el archivo: {exc}")
            print("Se usaran las listas predefinidas.")
            return predefined_wordlists, "predefined"

    print("Se usaran las listas predefinidas del script.")
    return predefined_wordlists, "predefined"
