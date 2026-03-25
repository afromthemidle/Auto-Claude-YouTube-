"""
Subidor de videos a YouTube usando la YouTube Data API v3.
Maneja autenticación OAuth2 y subida de videos con metadatos completos.
Soporta credenciales desde variables de entorno (para despliegue en Render/cloud).
"""

import os
import logging
import json
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def _get_client_secrets_dict() -> dict:
    """Obtiene el dict de client_secrets desde env var o archivo."""
    env_json = os.getenv("YOUTUBE_CLIENT_SECRET_JSON")
    if env_json:
        return json.loads(env_json)

    client_secrets_file = os.getenv(
        "YOUTUBE_CLIENT_SECRETS_FILE", "credentials/client_secret.json"
    )
    if Path(client_secrets_file).exists():
        with open(client_secrets_file) as f:
            return json.load(f)

    raise FileNotFoundError(
        "Credenciales de YouTube no encontradas. "
        "Configura YOUTUBE_CLIENT_SECRET_JSON como variable de entorno "
        "o coloca el archivo en credentials/client_secret.json"
    )


def _get_saved_token() -> Credentials | None:
    """Carga el token guardado desde env var o archivo."""
    token_json = os.getenv("YOUTUBE_TOKEN_JSON")
    if token_json:
        return Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    token_file = os.getenv("YOUTUBE_TOKEN_FILE", "credentials/youtube_token.json")
    if Path(token_file).exists():
        return Credentials.from_authorized_user_file(token_file, SCOPES)

    return None


def _save_token(creds: Credentials):
    """Guarda el token en archivo."""
    token_file = os.getenv("YOUTUBE_TOKEN_FILE", "credentials/youtube_token.json")
    Path(token_file).parent.mkdir(parents=True, exist_ok=True)
    with open(token_file, "w") as f:
        f.write(creds.to_json())
    logger.info(f"Token guardado en {token_file}")
    logger.info("Copia este JSON a la variable YOUTUBE_TOKEN_JSON en Render:")
    logger.info(creds.to_json())


def get_authenticated_service():
    """
    Autentica con YouTube API usando OAuth2.
    Lee credenciales desde variables de entorno o archivos locales.
    """
    creds = _get_saved_token()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Renovando token de YouTube...")
            creds.refresh(Request())
            _save_token(creds)
        else:
            raise RuntimeError(
                "YouTube no autenticado. Visita /api/youtube-auth en el dashboard "
                "para iniciar el proceso de autenticación."
            )

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)


def start_oauth_flow(redirect_uri: str) -> str:
    """Inicia el flujo OAuth y retorna la URL de autorización de Google."""
    from google_auth_oauthlib.flow import Flow
    client_config = _get_client_secrets_dict()
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    return auth_url


def finish_oauth_flow(code: str, redirect_uri: str) -> Credentials:
    """Finaliza el flujo OAuth con el código recibido del callback de Google."""
    from google_auth_oauthlib.flow import Flow
    client_config = _get_client_secrets_dict()
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    _save_token(creds)
    return creds


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

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": category_id,
            "defaultLanguage": "es",
            "defaultAudioLanguage": "es",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 10,
    )

    logger.info(f"Iniciando subida a YouTube: {title}")
    logger.info(f"Archivo: {video_path} ({Path(video_path).stat().st_size / 1024 / 1024:.1f} MB)")

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

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
    try:
        creds = _get_saved_token()
        return creds is not None
    except Exception:
        return False


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
