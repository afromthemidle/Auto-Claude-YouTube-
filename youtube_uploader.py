"""
Subidor de videos a YouTube usando la YouTube Data API v3.
Maneja autenticación OAuth2 y subida de videos con metadatos completos.
"""

import os
import logging
import json
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_authenticated_service():
    """
    Autentica con YouTube API usando OAuth2.
    En la primera ejecución, abre un navegador para autorización.
    Las credenciales se guardan para usos futuros.
    """
    client_secrets_file = os.getenv(
        "YOUTUBE_CLIENT_SECRETS_FILE", "credentials/client_secret.json"
    )
    token_file = os.getenv("YOUTUBE_TOKEN_FILE", "credentials/youtube_token.json")

    if not Path(client_secrets_file).exists():
        raise FileNotFoundError(
            f"Archivo de credenciales de YouTube no encontrado: {client_secrets_file}\n"
            "Descárgalo desde Google Cloud Console > APIs > Credenciales > OAuth 2.0"
        )

    creds = None

    # Cargar token existente
    if Path(token_file).exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Renovar o crear nuevo token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Renovando token de YouTube...")
            creds.refresh(Request())
        else:
            logger.info("Iniciando flujo de autenticación OAuth2 para YouTube...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            # En servidor sin GUI, usar autenticación por consola
            creds = flow.run_local_server(
                port=8080,
                prompt="consent",
                open_browser=True,
            )

        # Guardar el token
        Path(token_file).parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
        logger.info(f"Token de YouTube guardado en {token_file}")

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str = None,
    episode_number: int = 1,
) -> dict:
    """
    Sube el video a YouTube con todos sus metadatos.
    Retorna el ID y URL del video publicado.
    """
    youtube = get_authenticated_service()

    category_id = os.getenv("YOUTUBE_CATEGORY_ID", "22")
    privacy = os.getenv("YOUTUBE_PRIVACY", "public")

    # Metadatos del video
    body = {
        "snippet": {
            "title": title[:100],  # YouTube limita a 100 caracteres
            "description": description[:5000],  # YouTube limita a 5000 caracteres
            "tags": tags[:500],  # Limitar tags
            "categoryId": category_id,
            "defaultLanguage": "es",
            "defaultAudioLanguage": "es",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    # Configurar la subida del archivo
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,  # Subida resumible para archivos grandes
        chunksize=1024 * 1024 * 10,  # Chunks de 10MB
    )

    logger.info(f"Iniciando subida a YouTube: {title}")
    logger.info(f"Archivo: {video_path} ({Path(video_path).stat().st_size / 1024 / 1024:.1f} MB)")

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    # Subida con progreso
    video_id = None
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            logger.info(f"Subida: {progress}%")

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info(f"Video subido exitosamente: {video_url}")

    # Subir miniatura personalizada
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            logger.info("Subiendo miniatura personalizada...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg"),
            ).execute()
            logger.info("Miniatura personalizada subida.")
        except HttpError as e:
            logger.warning(f"No se pudo subir miniatura (puede requerir canal verificado): {e}")

    return {
        "video_id": video_id,
        "video_url": video_url,
        "title": title,
        "privacy": privacy,
        "published_at": datetime.utcnow().isoformat(),
    }


def check_youtube_auth() -> bool:
    """Verifica si la autenticación de YouTube está configurada."""
    token_file = os.getenv("YOUTUBE_TOKEN_FILE", "credentials/youtube_token.json")
    client_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "credentials/client_secret.json")
    return Path(token_file).exists() and Path(client_file).exists()


def get_channel_info() -> dict:
    """Obtiene información básica del canal de YouTube autenticado."""
    try:
        youtube = get_authenticated_service()
        response = youtube.channels().list(part="snippet,statistics", mine=True).execute()
        if response.get("items"):
            channel = response["items"][0]
            return {
                "id": channel["id"],
                "name": channel["snippet"]["title"],
                "subscribers": channel["statistics"].get("subscriberCount", "N/A"),
                "video_count": channel["statistics"].get("videoCount", "N/A"),
            }
    except Exception as e:
        logger.error(f"Error obteniendo info del canal: {e}")
    return {}
