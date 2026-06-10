"""Compone la placa 1080x1350 con la plantilla fija de la cuenta:
título, dos paneles (celeste Argentina / verde-oro Australia), barras
comparativas cuando el dato es numérico, insight y fuentes al pie."""

from PIL import Image, ImageDraw, ImageFont

import theme


def _font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(theme.find_font(kind), size)


def _text_w(draw, text, font):
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def _fit_font(draw, text, kind, max_size, max_width):
    """Achica la tipografía hasta que el texto entre en max_width."""
    size = max_size
    font = _font(kind, size)
    while _text_w(draw, text, font) > max_width and size > 18:
        size -= 2
        font = _font(kind, size)
    return font


def _wrap(draw, text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if _text_w(draw, candidate, font) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _centered(draw, y, text, font, fill, canvas_w=theme.CANVAS_W):
    draw.text(((canvas_w - _text_w(draw, text, font)) / 2, y), text, font=font, fill=fill)


def render_card(item: dict, out_path: str) -> str:
    W, H, M = theme.CANVAS_W, theme.CANVAS_H, theme.MARGIN
    C = theme.COLORS
    img = Image.new("RGB", (W, H), C["background"])
    draw = ImageDraw.Draw(img)

    _centered(draw, M, theme.HANDLE, _font("regular", theme.SIZES["handle"]), C["text_muted"])

    y = M + 70
    title_font = _font("bold", theme.SIZES["title"])
    for line in _wrap(draw, item["titulo"].upper(), title_font, W - 2 * M):
        _centered(draw, y, line, title_font, C["text"])
        y += theme.SIZES["title"] + 10
    y += 30

    # Paneles de país
    panel_w = (W - 2 * M - 40) // 2
    panel_h = 330
    panels = [
        (M, "ARGENTINA", C["argentina"], C["argentina_dark"], item["dato_argentina"]),
        (M + panel_w + 40, "AUSTRALIA", C["australia"], C["australia_gold"], item["dato_australia"]),
    ]
    for x, name, color, stripe, fact in panels:
        draw.rounded_rectangle([x, y, x + panel_w, y + panel_h], radius=28, fill=C["card"])
        draw.rounded_rectangle([x, y, x + panel_w, y + 16], radius=8, fill=stripe)

        name_font = _font("bold", theme.SIZES["country"])
        draw.text((x + (panel_w - _text_w(draw, name, name_font)) / 2, y + 48),
                  name, font=name_font, fill=color)

        value_font = _fit_font(draw, fact["valor"], "bold", theme.SIZES["value"], panel_w - 48)
        vy = y + 140
        for line in _wrap(draw, fact["valor"], value_font, panel_w - 48):
            draw.text((x + (panel_w - _text_w(draw, line, value_font)) / 2, vy),
                      line, font=value_font, fill=C["text"])
            vy += value_font.size + 6

        year_font = _font("regular", theme.SIZES["source"])
        year = f"({fact['anio']})"
        draw.text((x + (panel_w - _text_w(draw, year, year_font)) / 2, y + panel_h - 56),
                  year, font=year_font, fill=C["text_muted"])
    y += panel_h + 50

    # Barras comparativas si ambos valores son numéricos
    ar, au = item["dato_argentina"].get("valor_num"), item["dato_australia"].get("valor_num")
    if isinstance(ar, (int, float)) and isinstance(au, (int, float)) and max(ar, au) > 0:
        bar_max = W - 2 * M - 200
        for value, color in ((ar, C["argentina"]), (au, C["australia_gold"])):
            bar_w = max(int(bar_max * value / max(ar, au)), 24)
            draw.rounded_rectangle([M, y, M + bar_w, y + 36], radius=18, fill=color)
            label_font = _font("bold", 30)
            draw.text((M + bar_w + 20, y + 2), f"{value:g}", font=label_font, fill=color)
            y += 56
        y += 30

    # Insight
    insight_font = _font("regular", theme.SIZES["insight"])
    for line in _wrap(draw, item["insight"], insight_font, W - 2 * M):
        _centered(draw, y, line, insight_font, C["accent"])
        y += theme.SIZES["insight"] + 12

    # Fuentes al pie: la credibilidad es parte de la marca
    src_font = _font("regular", theme.SIZES["source"])
    sources = (f"Fuentes: {item['dato_argentina']['fuente']} · "
               f"{item['dato_australia']['fuente']}")
    for i, line in enumerate(reversed(_wrap(draw, sources, src_font, W - 2 * M))):
        _centered(draw, H - M - 30 * (i + 1), line, src_font, C["text_muted"])

    img.save(out_path, quality=95)
    return out_path
