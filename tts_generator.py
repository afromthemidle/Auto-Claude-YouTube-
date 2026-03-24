"""
Generador de audio usando ElevenLabs TTS.
Produce voz muy realista en español para el podcast.
"""

import os
import logging
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

logger = logging.getLogger(__name__)

# Voces de ElevenLabs recomendadas para español (IDs de voces multilingües)
# El usuario puede cambiar ELEVENLABS_VOICE_ID en .env para elegir su voz preferida
RECOMMENDED_VOICES = {
    "Adam": "pNInz6obpgDQGcFmaJgB",        # Voz masculina, cálida
    "Antoni": "ErXwobaYiN019PkySvjV",       # Voz masculina, bien articulada
    "Arnold": "VR6AewLTigWG4xSOukaG",       # Voz masculina, potente
    "Callum": "N2lVS1w4EtoT3dr4eOWO",       # Voz masculina, narración
    "Charlie": "IKne3meq5aSn9XLyUdCD",      # Voz masculina, conversacional
}


def get_elevenlabs_client() -> ElevenLabs:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY no configurada en .env")
    return ElevenLabs(api_key=api_key)


def generate_audio(script: str, output_path: str, episode_number: int) -> str:
    """
    Convierte el guión de texto a audio usando ElevenLabs.
    Divide el guión en fragmentos si supera el límite de la API.
    """
    client = get_elevenlabs_client()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")

    logger.info(f"Generando audio para episodio {episode_number} con voz {voice_id}")

    # Configuración de voz optimizada para podcast en español
    voice_settings = VoiceSettings(
        stability=0.71,          # Estabilidad alta para narración consistente
        similarity_boost=0.85,   # Alta similitud con la voz original
        style=0.35,              # Algo de expresividad sin exagerar
        use_speaker_boost=True,  # Mejora la claridad del hablante
    )

    # ElevenLabs soporta hasta ~5000 caracteres por llamada en el plan gratuito
    # Para textos largos, dividimos y concatenamos
    audio_chunks = []
    max_chunk_size = 4500

    # Dividir el guión en fragmentos por párrafos completos
    paragraphs = script.split("\n\n")
    current_chunk = ""
    chunks = []

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    logger.info(f"Guión dividido en {len(chunks)} fragmento(s) para TTS")

    # Generar audio para cada fragmento
    all_audio_bytes = b""
    for i, chunk in enumerate(chunks):
        logger.info(f"Generando fragmento de audio {i+1}/{len(chunks)} ({len(chunk)} caracteres)")
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=chunk,
            model_id="eleven_multilingual_v2",   # Mejor modelo para español
            voice_settings=voice_settings,
            output_format="mp3_44100_128",         # Calidad de podcast estándar
        )
        # El resultado es un generador de bytes
        chunk_bytes = b"".join(audio_generator)
        all_audio_bytes += chunk_bytes

    # Guardar el audio completo
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(all_audio_bytes)

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Audio guardado: {output_path} ({file_size_mb:.2f} MB)")
    return str(output_path)


def get_audio_duration_seconds(audio_path: str) -> float:
    """Obtiene la duración del audio en segundos usando ffprobe."""
    import subprocess
    import json

    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", audio_path
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.warning("ffprobe no disponible, usando duración estimada")
        # Estimación: ~150 palabras por minuto
        return 600.0  # 10 minutos por defecto

    data = json.loads(result.stdout)
    for stream in data.get("streams", []):
        if "duration" in stream:
            return float(stream["duration"])

    return 600.0
