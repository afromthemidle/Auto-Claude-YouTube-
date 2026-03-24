"""
Creador de video para el podcast usando FFmpeg.
Combina la imagen de fondo animada con el audio del podcast.
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_ffmpeg():
    """Verifica que FFmpeg esté instalado."""
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg no está instalado. Instálalo con: sudo apt install ffmpeg"
        )


def create_podcast_video(
    audio_path: str,
    thumbnail_path: str,
    output_path: str,
    episode_number: int,
    character_name: str,
) -> str:
    """
    Crea el video del podcast combinando:
    - Imagen de fondo (thumbnail del episodio) como fondo estático
    - Audio del guión narrado
    - Overlay con waveform animada (visualizador de audio)

    El video resultante es en formato 1920x1080 (Full HD) para YouTube.
    """
    check_ffmpeg()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Crear el video con FFmpeg
    # - Escala la imagen al tamaño 1920x1080 con padding
    # - Añade el audio
    # - Añade un visualizador de audio (showwaves) como overlay
    # - Añade subtítulo del episodio en la parte inferior

    episode_text = f"Episodio {episode_number}: {character_name}"

    # Comando FFmpeg para crear video profesional de podcast
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",                                          # Sobrescribir si existe
        "-loop", "1",                                  # Loop de imagen
        "-i", str(thumbnail_path),                     # Imagen de fondo
        "-i", str(audio_path),                         # Audio del podcast
        "-filter_complex",
        (
            # 1. Escalar imagen a 1920x1080 con padding negro si es necesario
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            "boxblur=3:1[bg];"

            # 2. Crear visualizador de audio (waveform)
            "[1:a]showwaves=s=1920x200:mode=cline:rate=25:"
            "colors=4CAF50|66BB6A|A5D6A7|E8F5E9[waves];"

            # 3. Crear fondo semi-transparente para el visualizador
            "color=c=black@0.6:s=1920x200[wavebg];"

            # 4. Combinar: fondo + wavebg en la parte inferior + waveform encima
            "[bg][wavebg]overlay=0:880[v1];"
            "[v1][waves]overlay=0:880[vout]"
        ),
        "-map", "[vout]",                              # Video procesado
        "-map", "1:a",                                 # Audio original
        "-c:v", "libx264",                             # Codec de video H.264
        "-preset", "medium",                           # Equilibrio calidad/velocidad
        "-crf", "23",                                  # Calidad de video (18-28, menor=mejor)
        "-c:a", "aac",                                 # Codec de audio AAC
        "-b:a", "192k",                                # Bitrate de audio (calidad alta)
        "-r", "25",                                    # 25 fps
        "-pix_fmt", "yuv420p",                        # Formato de pixel compatible
        "-movflags", "+faststart",                     # Optimizado para streaming
        "-shortest",                                   # Duración = duración del audio
        str(output_path),
    ]

    logger.info(f"Creando video para episodio {episode_number}...")
    logger.info(f"Comando FFmpeg: {' '.join(ffmpeg_cmd)}")

    result = subprocess.run(
        ffmpeg_cmd,
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hora máximo
    )

    if result.returncode != 0:
        logger.error(f"Error FFmpeg stderr: {result.stderr[-2000:]}")
        raise RuntimeError(f"FFmpeg falló con código {result.returncode}: {result.stderr[-500:]}")

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Video creado: {output_path} ({file_size_mb:.1f} MB)")
    return str(output_path)


def get_video_duration(video_path: str) -> float:
    """Obtiene la duración del video en segundos."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(video_path)
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        import json
        data = json.loads(result.stdout)
        duration = data.get("format", {}).get("duration")
        if duration:
            return float(duration)
    return 0.0
