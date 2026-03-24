"""
Generador de audio usando edge-tts (Microsoft Edge Neural TTS).
100% gratuito, sin API key, voces neurales muy realistas en español.
"""

import asyncio
import logging
import os
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)

# Voces neurales en español disponibles en edge-tts (todas gratuitas)
# Ejecuta `edge-tts --list-voices | grep es-` para ver todas
SPANISH_VOICES = {
    "es-ES-AlvaroNeural":   "Álvaro - España (masculino, cálido) ⭐ Recomendado",
    "es-ES-ElviraNeural":   "Elvira - España (femenino, clara)",
    "es-MX-JorgeNeural":    "Jorge - México (masculino, profundo)",
    "es-MX-DaliaNeural":    "Dalia - México (femenino, natural)",
    "es-AR-TomasNeural":    "Tomás - Argentina (masculino)",
    "es-AR-ElenaNeural":    "Elena - Argentina (femenino)",
    "es-CO-GonzaloNeural":  "Gonzalo - Colombia (masculino)",
    "es-CO-SalomeNeural":   "Salomé - Colombia (femenino)",
}

# Voz por defecto: Álvaro de España, ideal para podcast narrativo
DEFAULT_VOICE = os.getenv("TTS_VOICE", "es-ES-AlvaroNeural")

# Velocidad de habla: valores posibles "+10%", "-5%", "+0%", etc.
DEFAULT_RATE = os.getenv("TTS_RATE", "-5%")   # Ligeramente más lento para podcast

# Volumen: "+0%", "+10%", "-10%"
DEFAULT_VOLUME = os.getenv("TTS_VOLUME", "+10%")


async def _synthesize_to_file(text: str, output_path: str, voice: str, rate: str, volume: str):
    """Corrutina interna que llama a edge-tts y guarda el MP3."""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(output_path)


def generate_audio(script: str, output_path: str, episode_number: int) -> str:
    """
    Convierte el guión a audio MP3 usando edge-tts (Microsoft neural TTS).
    Completamente gratuito, sin límite de caracteres por llamada.
    """
    voice = DEFAULT_VOICE
    rate = DEFAULT_RATE
    volume = DEFAULT_VOLUME

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generando audio con edge-tts: voz={voice}, rate={rate}")
    logger.info(f"Longitud del guión: {len(script)} caracteres")

    # Limpiar el texto para mejor pronunciación
    clean_script = _clean_script_for_tts(script)

    # edge-tts es async; lo ejecutamos en el event loop actual o uno nuevo
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop corriendo (FastAPI), usar run_in_executor con nuevo loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(_run_async_synthesis, clean_script, str(output_path), voice, rate, volume)
                future.result(timeout=600)
        else:
            loop.run_until_complete(
                _synthesize_to_file(clean_script, str(output_path), voice, rate, volume)
            )
    except RuntimeError:
        # No hay event loop, crear uno nuevo
        asyncio.run(_synthesize_to_file(clean_script, str(output_path), voice, rate, volume))

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("edge-tts no generó el archivo de audio correctamente")

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Audio guardado: {output_path} ({file_size_mb:.2f} MB)")
    return str(output_path)


def _run_async_synthesis(text: str, output_path: str, voice: str, rate: str, volume: str):
    """Ejecuta la síntesis en un nuevo event loop (para usar desde threads)."""
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        new_loop.run_until_complete(
            _synthesize_to_file(text, output_path, voice, rate, volume)
        )
    finally:
        new_loop.close()


def _clean_script_for_tts(script: str) -> str:
    """Limpia el guión para mejor pronunciación TTS."""
    import re
    # Eliminar markdown (asteriscos, ##, etc.)
    script = re.sub(r'\*+([^*]+)\*+', r'\1', script)  # **texto** → texto
    script = re.sub(r'#{1,6}\s+', '', script)           # ## Título → Título
    script = re.sub(r'_+([^_]+)_+', r'\1', script)     # _texto_ → texto
    # Eliminar corchetes y paréntesis de anotaciones
    script = re.sub(r'\[.*?\]', '', script)
    # Normalizar espacios y líneas en blanco
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


async def list_available_voices() -> list[dict]:
    """Lista todas las voces en español disponibles en edge-tts."""
    voices = await edge_tts.list_voices()
    spanish = [v for v in voices if v["Locale"].startswith("es-")]
    return [
        {
            "voice_id": v["ShortName"],
            "name": v["FriendlyName"],
            "locale": v["Locale"],
            "gender": v["Gender"],
        }
        for v in spanish
    ]
