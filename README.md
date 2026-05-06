# sopa_libros

Generador en Python para crear libros de sopas de letras orientados a Amazon KDP. El proyecto permite generar puzzles, soluciones resaltadas, páginas temáticas, índice, instrucciones, portadas de bloque e interiores finales en PDF.

El repositorio tiene dos formas principales de uso:

1. **Modo simple** (`main.py`): genera puzzles a partir de listas básicas de palabras.
2. **Modo temático** (`main_thematic.py`): genera un libro más completo a partir de un archivo con bloques, títulos, facts y listas de palabras.

---

## 1. Requisitos

### Software necesario

- Python 3.10 o superior recomendado.
- pip.
- Un entorno virtual de Python recomendado.

### Dependencias Python

El proyecto usa principalmente:

- `Pillow`: renderizado de páginas e imágenes.
- `reportlab`: creación del PDF final.

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

Para desarrollo del proyecto, incluyendo tests, cobertura y lint, usa la guia
de entorno en:

```text
docs/development.md
```

---

## 2. Instalación desde cero

Clona el repositorio:

```bash
git clone https://github.com/Nachobt98/sopa_libros.git
cd sopa_libros
```

Crea un entorno virtual:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Comprueba que Python puede importar las dependencias:

```bash
python -c "from PIL import Image; import reportlab; print('OK')"
```

---

## 3. Estructura del proyecto

Nota: la estructura interna se organiza por responsabilidades. El codigo vive
principalmente bajo `wordsearch/config/`, `wordsearch/generation/`,
`wordsearch/rendering/`, `wordsearch/parsing/`, `wordsearch/domain/`,
`wordsearch/io/`, `wordsearch/cli/`, `wordsearch/utils/` y
`wordsearch/validation/`.

```text
sopa_libros/
├─ main.py                         # Generador simple/interactivo
├─ main_thematic.py                # Generador temático completo
├─ requirements.txt                # Dependencias Python
├─ README.md                       # Documentación de uso
├─ wordsearch/
│  ├─ __init__.py
│  ├─ config/                      # Layout, fuentes y rutas base
│  ├─ domain/                      # Dataclasses y modelos de dominio
│  ├─ generation/                  # Grid, batch generation y orquestación
│  ├─ io/                          # Carga de entradas externas
│  ├─ parsing/                     # Parsers de archivos de entrada
│  ├─ rendering/                   # Renderizado de páginas e imágenes
│  ├─ utils/                       # Utilidades generales
│  ├─ validation/                  # Validadores por flujo
│  └─ text_normalization.py        # Normalización de palabras para el grid
├─ wordlists/
│  ├─ book_thematic.txt            # Ejemplo temático sin bloques
│  ├─ book_block.txt               # Ejemplo temático con bloques
│  ├─ libro1.txt                   # Libro temático extenso
│  ├─ libro2.txt                   # Variante/versión parcial de libro temático
│  └─ tiburones_10_sopas.txt       # Ejemplo simple en español
└─ fonts/
   ├─ montserrat/
   └─ abril_fatface/
```

---

## 4. Conceptos principales

### Puzzle

Una sopa de letras individual con:

- título opcional en modo temático;
- fact opcional en modo temático;
- lista de palabras;
- grid generado automáticamente;
- página de solución.

### Grid

Matriz de letras donde se colocan las palabras. El tamaño depende de la dificultad y de la elección del usuario.

### Solución

Página donde las palabras aparecen resaltadas sobre el grid mediante una cápsula visual.

### Bloque temático

Sección editorial del libro. Por ejemplo:

- `Foundations of Black History`
- `Civil Rights & Social Justice`
- `Black Arts, Music & Literature`

Cada bloque puede tener su propia portada y fondo.

### Fun fact

Texto breve mostrado en la página del puzzle. Sirve para añadir valor editorial al libro.

---

## 5. Modo simple: `main.py`

Usa este modo para pruebas rápidas o libros sencillos sin bloques editoriales.

Ejecuta:

```bash
python main.py
```

El script pedirá:

1. Título del libro.
2. Dificultad.
3. Tamaño del grid.
4. Origen de palabras.
5. Número de puzzles.

### Orígenes de palabras soportados

El modo simple permite:

1. Usar listas predefinidas internas.
2. Escribir una lista manual separada por comas.
3. Cargar un `.txt` desde `wordlists/`.

### Formato de archivo simple

Un archivo simple contiene una palabra por línea. Cada bloque separado por una línea en blanco se interpreta como una lista distinta.

Ejemplo:

```text
tiburon
dientes
cartilago
depredador
oceano

martillo
sensor
ojos
cefalico
arena
```

Cada bloque genera una sopa diferente cuando se usa desde archivo `.txt`.

Archivo de ejemplo:

```text
wordlists/tiburones_10_sopas.txt
```

---

## 6. Modo temático: `main_thematic.py`

Este es el modo recomendado para crear libros más profesionales.

Ejecuta:

```bash
python main_thematic.py
```

El script pedirá:

1. Título del libro.
2. Ruta del archivo temático.
3. Dificultad.
4. Tamaño del grid.

Si no introduces ruta, usa por defecto:

```text
wordlists/book_thematic.txt
```

### Qué genera el modo temático

El flujo temático puede generar:

- página de índice;
- página de instrucciones;
- portadas de bloque;
- puzzles con título y fun fact;
- soluciones;
- portada de soluciones;
- PDF final.

### Ejecución recomendada

```bash
python main_thematic.py
```

Cuando pregunte por el archivo, puedes usar por ejemplo:

```text
wordlists/book_block.txt
```

O:

```text
wordlists/libro1.txt
```

---

## 7. Formato de archivo temático

Los archivos temáticos usan bloques `[Block]` y puzzles `[Puzzle]`.

### Bloque temático

```text
[Block]
name: Black History Foundations
background: assets/world.png
[/Block]
```

Campos:

- `name`: nombre visible del bloque.
- `background`: ruta opcional del fondo usado por ese bloque.

Los puzzles que aparecen después del bloque heredan ese nombre y fondo hasta que aparezca otro `[Block]`.

### Puzzle temático

```text
[Puzzle]
title: Black Inventors
fact: Garrett Morgan invented both the traffic light and a type of gas mask, saving countless lives.
words:
Garrett Morgan
Traffic Light
Gas Mask
Innovation
Patent
Safety
Invention
Engineer
Design
Experiment
Prototype
Progress
Impact
Technology
Creativity
[/Puzzle]
```

Campos obligatorios:

- `title:` título del puzzle.
- `fact:` texto breve que aparecerá en la caja `FUN FACT`.
- `words:` lista de palabras/frases, una por línea.

### Reglas importantes

- Cada puzzle debe cerrarse con `[/Puzzle]`.
- Cada bloque debe cerrarse con `[/Block]`.
- Las palabras pueden contener espacios en modo temático; internamente se limpian para el grid.
- La versión visible en la lista de palabras conserva el texto original.

---

## 8. Dificultades

El proyecto soporta tres niveles.

### EASY

- Grid recomendado: 8 a 12.
- Direcciones: derecha y abajo.
- Sin palabras invertidas.

### MEDIUM

- Grid recomendado: 12 a 15.
- Direcciones: derecha, abajo y diagonales descendentes.
- Sin palabras invertidas.

### HARD

- Grid recomendado: 15 a 20.
- Direcciones: horizontales, verticales y diagonales en ambos sentidos.
- Permite palabras invertidas mediante direcciones negativas.

---

## 9. Salida generada

Los archivos se guardan dentro de:

```text
output_puzzles_kdp/
```

Cada libro genera una subcarpeta basada en el título. Por ejemplo:

```text
output_puzzles_kdp/black_culture_word_search_vol_1/
```

Dentro pueden aparecer:

- PNGs de puzzles.
- PNGs de soluciones.
- PNGs de índice/instrucciones/bloques.
- PDF final.

La carpeta de salida está ignorada por Git para evitar subir archivos pesados generados automáticamente.

---

## 10. Tamaño KDP y layout

La configuración principal está en:

```text
wordsearch/config/layout.py
wordsearch/config/fonts.py
wordsearch/config/paths.py
```

Actualmente el proyecto está configurado para:

```text
Trim size: 6 x 9 pulgadas
DPI: 300
```

La página se renderiza como imagen a 300 DPI y luego se inserta en el PDF final.

Parámetros importantes:

- `TRIM_W_IN`
- `TRIM_H_IN`
- `DPI`
- `PAGE_W_PX`
- `PAGE_H_PX`
- `SAFE_LEFT`
- `SAFE_RIGHT`
- `SAFE_TOP`
- `SAFE_BOTTOM`

---

## 11. Fuentes

El layout referencia estas fuentes:

```text
fonts/montserrat/static/Montserrat-Regular.ttf
fonts/montserrat/static/Montserrat-Medium.ttf
fonts/abril_fatface/AbrilFatface-Regular.ttf
```

Si las fuentes no existen en esas rutas, el código usa una fuente por defecto de Pillow. El libro seguirá generándose, pero el resultado visual puede cambiar bastante.

Las carpetas de fuentes incluyen licencias OFL, pero los archivos `.ttf` y `.otf` pueden estar ignorados por Git según `.gitignore`.

Para reproducir el diseño esperado:

1. Descarga Montserrat.
2. Coloca los `.ttf` en `fonts/montserrat/static/`.
3. Descarga Abril Fatface.
4. Coloca `AbrilFatface-Regular.ttf` en `fonts/abril_fatface/`.

---

## 12. Fondos y assets

Algunos archivos temáticos referencian fondos como:

```text
assets/world.png
```

Si el fondo existe, se usa como background de página/bloque. Si no existe, el renderizado cae a fondo blanco.

Para añadir fondos propios:

1. Crea carpeta `assets/` si no existe.
2. Añade imágenes `.png` o `.jpg`.
3. Referencia la ruta desde el archivo temático:

```text
[Block]
name: Black Arts, Music & Literature
background: assets/black_arts_bg.png
[/Block]
```

Recomendación: usa imágenes con buena resolución y proporción compatible con 6x9.

---

## 13. Ejemplos de uso rápido

### Generar libro simple de tiburones

```bash
python main.py
```

Cuando pregunte por palabras:

```text
3
wordlists/tiburones_10_sopas.txt
```

### Generar libro temático de prueba con bloques

```bash
python main_thematic.py
```

Cuando pregunte por archivo:

```text
wordlists/book_block.txt
```

### Generar libro temático grande

```bash
python main_thematic.py
```

Cuando pregunte por archivo:

```text
wordlists/libro1.txt
```

---

## 14. Problemas comunes

### `ModuleNotFoundError: No module named 'PIL'`

Falta Pillow.

Solución:

```bash
pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'reportlab'`

Falta ReportLab.

Solución:

```bash
pip install -r requirements.txt
```

### El diseño se ve raro o con otra tipografía

Probablemente faltan los `.ttf` esperados.

Revisa:

```text
fonts/montserrat/static/Montserrat-Regular.ttf
fonts/montserrat/static/Montserrat-Medium.ttf
fonts/abril_fatface/AbrilFatface-Regular.ttf
```

### El fondo no aparece

El archivo referenciado en `background:` no existe o la ruta es incorrecta.

Ejemplo:

```text
background: assets/world.png
```

Asegúrate de que esa ruta exista desde la raíz del proyecto.

### Un puzzle no se genera

Puede pasar si:

- hay demasiadas palabras;
- el grid es pequeño;
- una palabra es demasiado larga;
- la lista es demasiado densa;
- la dificultad elegida tiene pocas direcciones disponibles.

Prueba:

- aumentar el tamaño del grid;
- usar dificultad media o difícil;
- reducir número de palabras;
- acortar palabras demasiado largas.

---

## 15. Recomendaciones para crear buenos libros KDP

### Para puzzles

- Usa entre 10 y 18 palabras por puzzle.
- Evita palabras excesivamente largas si el grid es pequeño.
- Mantén coherencia temática por puzzle.
- Usa títulos claros y atractivos.

### Para fun facts

- Hazlos breves.
- Evita párrafos enormes.
- Prioriza datos interesantes y fáciles de leer.
- Revisa factualidad si el libro se va a publicar.

### Para bloques

- Usa nombres editoriales claros.
- Evita bloques con muy pocos puzzles.
- Usa fondos consistentes por bloque.
- Mantén una progresión lógica del libro.

---

## 16. Flujo recomendado de producción

1. Crear o editar un archivo temático en `wordlists/`.
2. Ejecutar `python main_thematic.py`.
3. Generar una versión de prueba con pocos puzzles.
4. Revisar visualmente PNGs y PDF.
5. Ajustar palabras, facts, fondos o dificultad.
6. Generar versión completa.
7. Revisar márgenes y legibilidad.
8. Subir a KDP solo cuando el PDF esté validado.

---

## 17. Estado actual del proyecto

El proyecto ya permite generar libros funcionales, pero todavía hay mejoras pendientes recomendables:

- seguir unificando el modo simple con la pipeline temática;
- extraer primitivas reutilizables adicionales de renderizado cuando aparezca duplicación real;
- documentar o automatizar instalación de fuentes;
- ampliar tests de validación, render orchestration y modo simple.

---

## 18. Comandos útiles

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar modo simple:

```bash
python main.py
```

Ejecutar modo temático:

```bash
python main_thematic.py
```

Ejecutar checks locales:

```bash
python -m ruff check .
python -m pytest --cov=wordsearch --cov-report=term-missing --cov-report=xml
```

Limpiar outputs generados:

### Windows PowerShell

```powershell
Remove-Item -Recurse -Force output_puzzles_kdp
```

### macOS / Linux

```bash
rm -rf output_puzzles_kdp
```

---

## 19. Licencias de fuentes

El repositorio incluye archivos de licencia OFL para fuentes como Montserrat y Abril Fatface. Antes de publicar comercialmente, revisa que las fuentes usadas en el PDF estén correctamente licenciadas y disponibles en las rutas esperadas.
