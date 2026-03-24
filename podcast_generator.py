"""
Orquestador principal del podcast automático.
Coordina todos los pasos: script → audio → video → YouTube.
"""

import os
import logging
from datetime import datetime
from pathlib import Path

from database import (
    get_used_characters, add_used_character, get_next_episode_number,
    create_episode, update_episode, Episode,
)
from script_generator import select_character, generate_script, generate_title_and_description
from tts_generator import generate_audio
from thumbnail_generator import create_episode_thumbnail
from video_creator import create_podcast_video
from youtube_uploader import upload_video

logger = logging.getLogger(__name__)


def run_episode_generation() -> dict:
    """
    Pipeline completo para generar y publicar un nuevo episodio.
    Retorna un diccionario con el resultado del proceso.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO GENERACIÓN DE NUEVO EPISODIO DEL PODCAST")
    logger.info("=" * 60)

    episode_id = None
    episode_number = None

    try:
        # ─── PASO 1: Seleccionar personaje ───────────────────────────
        logger.info("[1/6] Seleccionando personaje vegetariano...")
        used_characters = get_used_characters()
        logger.info(f"Personajes ya usados: {len(used_characters)}")

        character_info = select_character(used_characters)
        character_name = character_info["nombre"]
        logger.info(f"Personaje seleccionado: {character_name}")

        # ─── PASO 2: Crear registro en BD ────────────────────────────
        episode_number = get_next_episode_number()
        ep = create_episode(
            episode_number=episode_number,
            character_name=character_name,
            nationality=character_info.get("nacionalidad"),
            profession=character_info.get("profesion"),
        )
        episode_id = ep.id
        update_episode(episode_id, status="generating")

        # Directorio de salida para este episodio
        output_dir = Path(f"output/ep_{episode_number:03d}_{character_name.replace(' ', '_')[:30]}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # ─── PASO 3: Generar guión con Claude ───────────────────────
        logger.info("[2/6] Generando guión con Claude AI...")
        script = generate_script(character_info, episode_number)
        logger.info(f"Guión generado: {len(script)} caracteres")

        metadata = generate_title_and_description(character_info, episode_number, script)
        youtube_title = metadata["titulo"]
        youtube_description = metadata["descripcion"]
        youtube_tags = metadata["tags"]

        update_episode(episode_id, script=script)

        # ─── PASO 4: Generar audio con ElevenLabs ───────────────────
        logger.info("[3/6] Generando audio con ElevenLabs TTS...")
        audio_path = str(output_dir / f"ep_{episode_number:03d}_audio.mp3")
        generate_audio(script, audio_path, episode_number)
        update_episode(episode_id, audio_path=audio_path)

        # ─── PASO 5: Crear miniatura y video ────────────────────────
        logger.info("[4/6] Creando miniatura del episodio...")
        thumbnail_path = str(output_dir / f"ep_{episode_number:03d}_thumbnail.jpg")
        create_episode_thumbnail(
            character_name=character_name,
            nationality=character_info.get("nacionalidad", ""),
            profession=character_info.get("profesion", ""),
            episode_number=episode_number,
            output_path=thumbnail_path,
        )
        update_episode(episode_id, thumbnail_path=thumbnail_path)

        logger.info("[5/6] Creando video con FFmpeg...")
        video_path = str(output_dir / f"ep_{episode_number:03d}_video.mp4")
        create_podcast_video(
            audio_path=audio_path,
            thumbnail_path=thumbnail_path,
            output_path=video_path,
            episode_number=episode_number,
            character_name=character_name,
        )
        update_episode(episode_id, video_path=video_path, status="uploading")

        # ─── PASO 6: Publicar en YouTube ────────────────────────────
        logger.info("[6/6] Publicando en YouTube...")
        yt_result = upload_video(
            video_path=video_path,
            title=youtube_title,
            description=youtube_description,
            tags=youtube_tags,
            thumbnail_path=thumbnail_path,
            episode_number=episode_number,
        )

        # ─── FINALIZAR ───────────────────────────────────────────────
        add_used_character(character_name)
        update_episode(
            episode_id,
            status="published",
            youtube_video_id=yt_result["video_id"],
            youtube_url=yt_result["video_url"],
            published_at=datetime.utcnow(),
        )

        logger.info("=" * 60)
        logger.info(f"✅ EPISODIO {episode_number} PUBLICADO EXITOSAMENTE")
        logger.info(f"   Personaje: {character_name}")
        logger.info(f"   YouTube URL: {yt_result['video_url']}")
        logger.info("=" * 60)

        return {
            "success": True,
            "episode_number": episode_number,
            "character_name": character_name,
            "youtube_url": yt_result["video_url"],
            "video_id": yt_result["video_id"],
        }

    except Exception as e:
        logger.error(f"Error en generación del episodio: {e}", exc_info=True)

        if episode_id:
            update_episode(episode_id, status="error", error_message=str(e))

        return {
            "success": False,
            "episode_number": episode_number,
            "error": str(e),
        }
