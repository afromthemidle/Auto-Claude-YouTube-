"""
Generador de audio usando OpenAI TTS.
Usa la API de OpenAI (tts-1) con voces en español.
"""

import logging
import os
from pathlib import Path

from openai import OpenAI

logger = logging.getLogger(__name__)

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Voz por defecto: "onyx" suena natural para podcast en español
# Opciones: alloy, echo, fable, onyx, nova, shimmer
DEFAULT_VOICE = os.getenv("TTS_VOICE", "onyx")

# Modelo TTS: tts-1 (rápido) o tts-1-hd (mayor calidad)
DEFAULT_MODEL = os.getenv("TTS_MODEL", "tts-1")


def generate_audio(script: str, output_path: str, episode_number: int) -> str:
    """
    Convierte el guión a audio MP3 usando OpenAI TTS.
    """
    voice = DEFAULT_VOICE
    model = DEFAULT_MODEL

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generando audio con OpenAI TTS: voz={voice}, modelo={model}")
    logger.info(f"Longitud del guión: {len(script)} caracteres")

    clean_script = _clean_script_for_tts(script)

    # OpenAI TTS tiene límite de 4096 caracteres por llamada
    # Si el guión es más largo, dividir en chunks
    chunks = _split_text(clean_script, max_chars=4000)
    logger.info(f"Dividido en {len(chunks)} chunk(s) para TTS")

    if len(chunks) == 1:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=chunks[0],
            response_format="mp3",
        )
        response.stream_to_file(str(output_path))
    else:
        # Generar chunks y concatenar con ffmpeg
        import subprocess
        chunk_paths = []
        for i, chunk in enumerate(chunks):
            chunk_path = output_path.parent / f"_chunk_{episode_number}_{i}.mp3"
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=chunk,
                response_format="mp3",
            )
            response.stream_to_file(str(chunk_path))
            chunk_paths.append(str(chunk_path))

        # Concatenar con ffmpeg
        list_file = output_path.parent / f"_chunks_{episode_number}.txt"
        with open(list_file, "w") as f:
            for cp in chunk_paths:
                f.write(f"file '{cp}'\n")

        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
             "-c", "copy", str(output_path)],
            check=True, capture_output=True
        )

        # Limpiar archivos temporales
        for cp in chunk_paths:
            Path(cp).unlink(missing_ok=True)
        list_file.unlink(missing_ok=True)

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("OpenAI TTS no generó el archivo de audio correctamente")

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Audio guardado: {output_path} ({file_size_mb:.2f} MB)")
    return str(output_path)


def _split_text(text: str, max_chars: int = 4000) -> list[str]:
    """Divide el texto en chunks respetando los párrafos."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current)
            # Si el párrafo solo ya es demasiado largo, dividir por frases
            if len(para) > max_chars:
                sentences = para.split(". ")
                current = ""
                for s in sentences:
                    if len(current) + len(s) + 2 <= max_chars:
                        current += (". " if current else "") + s
                    else:
                        if current:
                            chunks.append(current)
                        current = s
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def _clean_script_for_tts(script: str) -> str:
    """Limpia el guión para mejor pronunciación TTS."""
    import re
    script = re.sub(r'\*+([^*]+)\*+', r'\1', script)
    script = re.sub(r'#{1,6}\s+', '', script)
    script = re.sub(r'_+([^_]+)_+', r'\1', script)
    script = re.sub(r'\[.*?\]', '', script)
    script = re.sub(r'\n{3,}', '\n\n', script)
    script = script.strip()
    return script


def get_audio_duration_seconds(audio_path: str) -> float:
    """Obtiene la duración del audio en segundos usando ffprobe."""
    import subprocess
    import json

    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", audio_path],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        for stream in data.get("streams", []):
            if "duration" in stream:
                return float(stream["duration"])
    return 600.0
