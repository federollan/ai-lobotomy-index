"""Configuración visual de las placas. Cambiá acá colores, fuentes y medidas
para que toda la cuenta mantenga la misma identidad."""

import os

# Formato retrato de Instagram (4:5)
CANVAS_W = 1080
CANVAS_H = 1350

COLORS = {
    "background": "#0E1B2A",      # azul noche, hace resaltar ambos paneles
    "card": "#13243A",
    "argentina": "#74ACDF",       # celeste bandera
    "argentina_dark": "#4A8BC4",
    "australia": "#00843D",       # verde nacional
    "australia_gold": "#FFCD00",  # dorado nacional
    "text": "#FFFFFF",
    "text_muted": "#8FA3B8",
    "accent": "#FFCD00",
}

# Primer path que exista gana; agregá tu tipografía de marca al inicio.
FONT_CANDIDATES = {
    "bold": [
        "assets/fonts/Brand-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
    "regular": [
        "assets/fonts/Brand-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
}

SIZES = {
    "title": 64,
    "country": 40,
    "value": 76,
    "value_small": 54,
    "insight": 36,
    "source": 24,
    "handle": 28,
}

MARGIN = 64
HANDLE = "@assessments.solutions"  # tu usuario de Instagram


def find_font(kind: str) -> str:
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No se encontró ninguna fuente para '{kind}'")
