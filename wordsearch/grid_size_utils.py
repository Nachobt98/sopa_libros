"""
Utilidad para preguntar y validar el tamaño del grid según la dificultad seleccionada.
"""

def ask_grid_size(settings):
    min_size = settings["grid_min"]
    max_size = settings["grid_max"]
    default_size = settings["grid_default"]
    prompt = f"Tamaño del grid [{min_size}-{max_size}, por defecto {default_size}]: "
    while True:
        raw = input(prompt).strip()
        if not raw:
            return default_size
        try:
            val = int(raw)
            if min_size <= val <= max_size:
                return val
            else:
                print(f"El tamaño debe estar entre {min_size} y {max_size} para esta dificultad.")
        except Exception:
            print("Por favor, introduce un número válido.")
