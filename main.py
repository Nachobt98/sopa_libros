"""
Script principal para generar libros de sopas de letras con niveles de dificultad.
"""

import os
from wordsearch.constants_and_layout import BASE_OUTPUT_DIR
from wordsearch.wordlist_utils import slugify, load_wordlists_from_txt
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

    # Listas de palabras
    predefined_wordlists = [
        ["gato", "perro", "casa", "luna", "sol", "arbol", "cielo", "mar"],
        ["python", "codigo", "amazon", "kdp", "libro", "puzzle", "print"],
    ]
    wordlists = predefined_wordlists  # Puedes añadir lógica para cargar desde txt

    # Número de puzzles
    total = 10
    try:
        total_raw = input("\n¿Cuántos puzzles quieres generar? [por defecto 10]: ").strip()
        if total_raw:
            total = int(total_raw)
    except Exception:
        pass

    puzzles = []
    solutions = []
    for i in range(1, total + 1):
        wl = wordlists[(i-1) % len(wordlists)].copy()
        import random
        random.shuffle(wl)
        while True:
            placed_result = place_words_on_grid(wl, difficulty=diff, grid_size=grid_size)
            if placed_result:
                grid, placed = placed_result
                break
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
