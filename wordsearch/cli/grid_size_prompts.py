"""Interactive prompts for selecting grid size."""

from __future__ import annotations


def ask_grid_size(settings):
    """Prompt for a grid size allowed by the selected difficulty settings."""
    min_size = settings["grid_min"]
    max_size = settings["grid_max"]
    default_size = settings["grid_default"]
    prompt = f"Tamaño del grid [{min_size}-{max_size}, por defecto {default_size}]: "

    while True:
        raw = input(prompt).strip()
        if not raw:
            return default_size
        try:
            value = int(raw)
            if min_size <= value <= max_size:
                return value
            print(f"El tamaño debe estar entre {min_size} y {max_size} para esta dificultad.")
        except Exception:
            print("Por favor, introduce un número válido.")
