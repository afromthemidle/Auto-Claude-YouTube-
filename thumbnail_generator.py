"""
Generador de miniaturas/thumbnails para cada episodio del podcast.
Crea imágenes atractivas con Pillow para el video de YouTube.
"""

import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)

# Paleta de colores para el podcast (tema verde/naturaleza)
COLORS = {
    "bg_dark":      "#0D1F0F",   # Verde muy oscuro (fondo)
    "bg_mid":       "#1A3A1C",   # Verde oscuro
    "accent_green": "#4CAF50",   # Verde brillante
    "accent_gold":  "#FFD700",   # Dorado para destacados
    "text_white":   "#FFFFFF",
    "text_light":   "#E8F5E9",
    "text_muted":   "#A5D6A7",
    "leaf_green":   "#66BB6A",
}

THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient_background(draw: ImageDraw, width: int, height: int):
    """Crea un fondo con gradiente verde oscuro."""
    bg_dark = hex_to_rgb(COLORS["bg_dark"])
    bg_mid = hex_to_rgb(COLORS["bg_mid"])

    for y in range(height):
        ratio = y / height
        r = int(bg_dark[0] + (bg_mid[0] - bg_dark[0]) * ratio)
        g = int(bg_dark[1] + (bg_mid[1] - bg_dark[1]) * ratio)
        b = int(bg_dark[2] + (bg_mid[2] - bg_dark[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_decorative_leaves(draw: ImageDraw, width: int, height: int):
    """Dibuja elementos decorativos de hojas."""
    leaf_color = (*hex_to_rgb(COLORS["leaf_green"]), 30)  # Muy transparente

    # Círculos decorativos en las esquinas (simulan hojas/naturaleza)
    positions = [
        (-80, -80, 200, 200),
        (width - 200, -80, width + 80, 200),
        (-80, height - 200, 200, height + 80),
        (width - 200, height - 200, width + 80, height + 80),
    ]
    for pos in positions:
        draw.ellipse(pos, fill=(*hex_to_rgb(COLORS["accent_green"]), 15))

    # Líneas decorativas
    for i in range(5):
        alpha = 20 - i * 3
        draw.arc(
            [width // 2 - 400 - i * 30, height // 2 - 350 - i * 30,
             width // 2 + 400 + i * 30, height // 2 + 350 + i * 30],
            start=200, end=340,
            fill=(*hex_to_rgb(COLORS["accent_green"]), max(alpha, 5)),
            width=2,
        )


def get_font(size: int, bold: bool = False) -> ImageFont:
    """Intenta cargar una fuente del sistema."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont, max_width: int, draw: ImageDraw) -> list[str]:
    """Divide el texto en líneas que caben en el ancho máximo."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_episode_thumbnail(
    character_name: str,
    nationality: str,
    profession: str,
    episode_number: int,
    output_path: str,
) -> str:
    """Crea la miniatura del episodio con diseño profesional."""
    img = Image.new("RGB", (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), color=hex_to_rgb(COLORS["bg_dark"]))
    draw = ImageDraw.Draw(img, "RGBA")

    # Fondo con gradiente
    create_gradient_background(draw, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)

    # Elementos decorativos
    draw_decorative_leaves(draw, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)

    # Barra superior de acento
    draw.rectangle([0, 0, THUMBNAIL_WIDTH, 8], fill=hex_to_rgb(COLORS["accent_green"]))

    # Barra inferior de acento
    draw.rectangle([0, THUMBNAIL_HEIGHT - 8, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT],
                   fill=hex_to_rgb(COLORS["accent_green"]))

    # Badge del episodio (esquina superior izquierda)
    badge_x, badge_y = 60, 40
    badge_w, badge_h = 220, 60
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=10,
        fill=hex_to_rgb(COLORS["accent_green"]),
    )
    ep_font = get_font(26, bold=True)
    ep_text = f"EPISODIO {episode_number}"
    draw.text((badge_x + 15, badge_y + 17), ep_text, font=ep_font, fill=hex_to_rgb(COLORS["bg_dark"]))

    # Emoji de hoja (símbolo del podcast)
    leaf_font = get_font(80, bold=False)
    draw.text((THUMBNAIL_WIDTH - 120, 30), "🌿", font=leaf_font, fill=hex_to_rgb(COLORS["accent_green"]))

    # Título del podcast
    podcast_font = get_font(32, bold=False)
    podcast_title = "PERSONAJES FAMOSOS VEGETARIANOS"
    podcast_title2 = "DEL MUNDO"
    draw.text((60, 130), podcast_title, font=podcast_font, fill=hex_to_rgb(COLORS["text_muted"]))
    draw.text((60, 170), podcast_title2, font=podcast_font, fill=hex_to_rgb(COLORS["text_muted"]))

    # Línea separadora
    draw.rectangle([60, 220, THUMBNAIL_WIDTH - 60, 224], fill=hex_to_rgb(COLORS["accent_green"]))

    # Nombre del personaje (texto principal, grande)
    name_font_size = 95 if len(character_name) < 15 else (75 if len(character_name) < 20 else 58)
    name_font = get_font(name_font_size, bold=True)
    name_lines = wrap_text(character_name, name_font, THUMBNAIL_WIDTH - 120, draw)

    name_y = 250
    for line in name_lines[:2]:  # Máximo 2 líneas
        # Sombra
        draw.text((62, name_y + 2), line, font=name_font, fill=(0, 0, 0, 180))
        # Texto principal
        draw.text((60, name_y), line, font=name_font, fill=hex_to_rgb(COLORS["text_white"]))
        name_y += name_font_size + 10

    # Profesión con icono
    prof_y = name_y + 20
    prof_font = get_font(38, bold=False)
    prof_text = f"★  {profession}"
    draw.text((60, prof_y), prof_text, font=prof_font, fill=hex_to_rgb(COLORS["accent_gold"]))

    # Nacionalidad
    nat_y = prof_y + 55
    nat_font = get_font(32, bold=False)
    nat_text = f"🌍  {nationality}"
    draw.text((60, nat_y), nat_text, font=nat_font, fill=hex_to_rgb(COLORS["text_muted"]))

    # Panel inferior con información del canal
    panel_y = THUMBNAIL_HEIGHT - 100
    draw.rectangle([0, panel_y, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT - 8],
                   fill=(*hex_to_rgb(COLORS["bg_dark"]), 200))

    channel_font = get_font(30, bold=True)
    draw.text((60, panel_y + 18), "🎙️  Podcast Vegetariano",
              font=channel_font, fill=hex_to_rgb(COLORS["accent_green"]))

    sub_font = get_font(24, bold=False)
    draw.text((THUMBNAIL_WIDTH - 320, panel_y + 22), "¡Suscríbete y activa 🔔!",
              font=sub_font, fill=hex_to_rgb(COLORS["text_muted"]))

    # Guardar
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "JPEG", quality=95)

    logger.info(f"Miniatura creada: {output_path}")
    return str(output_path)


def create_podcast_cover() -> str:
    """Crea la imagen de portada estática del podcast (usada como fondo del video)."""
    cover_path = Path("assets/podcast_cover.jpg")
    cover_path.parent.mkdir(parents=True, exist_ok=True)

    # Crear imagen de portada cuadrada (1:1) para el video background
    size = 1280
    img = Image.new("RGB", (size, size), color=hex_to_rgb(COLORS["bg_dark"]))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradiente
    for y in range(size):
        ratio = y / size
        bg1 = hex_to_rgb(COLORS["bg_dark"])
        bg2 = hex_to_rgb(COLORS["bg_mid"])
        r = int(bg1[0] + (bg2[0] - bg1[0]) * ratio)
        g = int(bg1[1] + (bg2[1] - bg1[1]) * ratio)
        b = int(bg1[2] + (bg2[2] - bg1[2]) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Círculos decorativos
    for i, (cx, cy, r) in enumerate([
        (size//2, size//2, 480),
        (size//2, size//2, 380),
        (size//2, size//2, 280),
    ]):
        alpha = 15 + i * 10
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(*hex_to_rgb(COLORS["accent_green"]), alpha),
            width=3,
        )

    # Título principal
    title_font = get_font(72, bold=True)
    title_lines = ["PERSONAJES", "FAMOSOS", "VEGETARIANOS", "DEL MUNDO"]
    total_h = len(title_lines) * 90
    start_y = (size - total_h) // 2 - 60

    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_w = bbox[2] - bbox[0]
        x = (size - text_w) // 2
        color = COLORS["accent_gold"] if i == 0 else COLORS["text_white"]
        draw.text((x + 2, start_y + i * 90 + 2), line, font=title_font, fill=(0, 0, 0, 150))
        draw.text((x, start_y + i * 90), line, font=title_font, fill=hex_to_rgb(color))

    # Emoji grande
    emoji_font = get_font(180)
    draw.text((size//2 - 90, start_y + 380), "🌿", font=emoji_font,
              fill=hex_to_rgb(COLORS["accent_green"]))

    # Subtítulo
    sub_font = get_font(40, bold=False)
    sub_text = "El podcast que inspira"
    bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    x = (size - (bbox[2] - bbox[0])) // 2
    draw.text((x, start_y + 600), sub_text, font=sub_font, fill=hex_to_rgb(COLORS["text_muted"]))

    img.save(str(cover_path), "JPEG", quality=95)
    logger.info(f"Portada del podcast creada: {cover_path}")
    return str(cover_path)
