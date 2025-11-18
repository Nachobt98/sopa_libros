"""
Lógica para colocar palabras en el grid según las reglas de dificultad.
Incluye: función principal de generación, validación de posiciones, etc.
"""

import random
from .difficulty_levels import difficulty_settings, DifficultyLevel

def place_words_on_grid(words, difficulty: DifficultyLevel, grid_size=None):
    settings = difficulty_settings[difficulty]
    size = grid_size if grid_size is not None else settings["grid_default"]
    directions = settings["directions"]
    allow_reversed = settings["allow_reversed"]
    max_attempts = 500
    grid = [['' for _ in range(size)] for _ in range(size)]
    placed = []
    words_sorted = sorted(words, key=lambda w: -len(w))
    attempts = 0

    for w in words_sorted:
        w = w.upper()
        candidates = []
        for r in range(size):
            for c in range(size):
                for dr, dc in directions:
                    candidates.append((r, c, dr, dc))

        random.shuffle(candidates)
        placed_flag = False

        for (r, c, dr, dc) in candidates:
            rr, cc = r, c
            fits = True

            for ch in w:
                if not (0 <= rr < size and 0 <= cc < size):
                    fits = False
                    break
                if grid[rr][cc] not in ('', ch):
                    fits = False
                    break
                rr += dr
                cc += dc

            if not fits:
                continue

            rr, cc = r, c
            for ch in w:
                grid[rr][cc] = ch
                rr += dr
                cc += dc

            placed.append((w, (r, c, dr, dc)))
            placed_flag = True
            break

        if not placed_flag:
            attempts += 1
            if attempts > max_attempts:
                return None
            return None

    for r in range(size):
        for c in range(size):
            if grid[r][c] == '':
                grid[r][c] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return grid, placed
