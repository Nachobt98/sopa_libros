"""
Script principal para generar libros de sopas de letras con niveles de dificultad.
"""

import os
from wordsearch.constants_and_layout import BASE_OUTPUT_DIR
from wordsearch.wordlist_utils import slugify, prompt_wordlists, validate_wordlists_for_grid
from wordsearch.grid_generation import place_words_on_grid
from wordsearch.image_rendering import render_page
from wordsearch.pdf_book_generation import generate_pdf
from wordsearch.difficulty_levels import DifficultyLevel, difficulty_settings
from wordsearch.grid_size_utils import ask_grid_size

# Puedes expandir este main para pedir dificultad, etc.
def main():
    book_title = input("Título del libro (p.ej. 'Wordsearch Animals Vol 1'): ").strip()
    if not book_title:
        book_title = "Wordsearch Book"
    slug = slugify(book_title)
    output_dir = os.path.join(BASE_OUTPUT_DIR, slug)
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nLos archivos se guardarán en: {output_dir}")

    # Selección de dificultad
    print("\nNiveles de dificultad disponibles:")
    for i, lvl in enumerate(DifficultyLevel, 1):
        print(f"{i}) {difficulty_settings[lvl]['name']} ({lvl.value})")
    diff_choice = input("Elige dificultad [1/2/3, por defecto 1]: ").strip() or "1"
    try:
        diff = list(DifficultyLevel)[int(diff_choice)-1]
    except Exception:
        diff = DifficultyLevel.EASY

    settings = difficulty_settings[diff]
    grid_size = ask_grid_size(settings)

    # -------------------------------------------------
    # 4) Listas de palabras
    # -------------------------------------------------
    predefined_wordlists = [
        ["gato", "perro", "casa", "luna", "sol", "arbol", "cielo", "mar"],
        ["python", "codigo", "amazon", "kdp", "libro", "puzzle", "print"],
    ]

    wordlists, source_type = prompt_wordlists(predefined_wordlists)

    # -------------------------------------------------
    # 5) Validar que todas las palabras caben en el grid
    # -------------------------------------------------
    problems = validate_wordlists_for_grid(wordlists, grid_size, remove_spaces=True)

    if problems:
        print("\n[ERROR] Se han encontrado palabras que no caben en el grid seleccionado.")
        print(f"Tamaño del grid: {grid_size}x{grid_size}")
        print("Revisa y corrige estas palabras en tus listas (o aumenta el tamaño del grid):\n")

        # Agrupar por lista para que sea más legible
        by_list = {}
        for p in problems:
            by_list.setdefault(p["list_index"], []).append(p)

        for li, items in by_list.items():
            print(f"  - Lista #{li + 1}:")
            for p in items:
                print(
                    f"      • '{p['word']}' (limpia: '{p['clean_word']}') "
                    f"tiene longitud {p['length']} > {grid_size}"
                )
            print()

        print("Corrige el archivo de palabras (o el tamaño de grid) y vuelve a ejecutar el script.")
        # Salir sin intentar generar nada
        return


    # -------------------------------------------------
    # 6) Número de puzzles
    # -------------------------------------------------
    if source_type == "txt":
        # Un puzzle por cada lista en el archivo
        total = len(wordlists)
        print(f"\nOrigen TXT detectado: se generarán {total} sopas de letras (una por lista).")
    else:
        default_total = 10
        while True:
            total_raw = input(f"\n¿Cuántos puzzles quieres generar? [por defecto {default_total}]: ").strip()
            if not total_raw:
                total = default_total
                break
            try:
                total = int(total_raw)
                if total <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Introduce un número entero positivo, por favor.")



    puzzles = []
    solutions = []
    for i in range(1, total + 1):
        wl = wordlists[(i-1) % len(wordlists)].copy()
        import random
        random.shuffle(wl)
        max_tries = 10
        placed_result = None
        for attempt in range(1, max_tries + 1):
            placed_result = place_words_on_grid(wl, difficulty=diff, grid_size=grid_size)
            if placed_result:
                break
            if not placed_result:
                print(f"[Aviso] Puzzle #{i}: no se ha podido generar un grid válido tras {max_tries} intentos.")
                print("Probablemente hay demasiadas palabras o la lista es muy densa para este tamaño de grid.")
                print("Ajusta manualmente la lista o el tamaño y vuelve a intentarlo.")
            continue
        grid, placed = placed_result

        sol_positions = set()
        for w, (r, c, dr, dc) in placed:
            rr, cc = r, c
            for _ in w:
                sol_positions.add((rr, cc))
                rr += dr
                cc += dc
        puzzle_img = render_page(
            grid, wl, i, is_solution=False,
            filename=os.path.join(output_dir, f"puzzle_{i}.png"),
            placed_words=None
        )
        solution_img = render_page(
            grid, wl, i, is_solution=True,
            filename=os.path.join(output_dir, f"puzzle_{i}_sol.png"),
            placed_words=placed
        )
        puzzles.append(puzzle_img)
        solutions.append(solution_img)
    pdf_name = f"{slug}.pdf"
    pdf_final = generate_pdf(puzzles, solutions, outname=os.path.join(output_dir, pdf_name))
    print("\nPDF generado:", pdf_final)

if __name__ == "__main__":
    main()
