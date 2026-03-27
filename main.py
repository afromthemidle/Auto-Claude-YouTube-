"""
Aplicación principal - Podcast Automático: Personajes Famosos Vegetarianos del Mundo
FastAPI + APScheduler para programar la generación diaria a las 23:20h
"""

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import get_all_episodes, get_episode, Episode
from podcast_generator import run_episode_generation
from youtube_uploader import check_youtube_auth, get_channel_info, start_oauth_flow, finish_oauth_flow

# ── Logging ──────────────────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)  # MUST exist before FileHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/podcast.log"),
    ],
)
logger = logging.getLogger(__name__)

# ── Scheduler global ─────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler()
generation_running = False


async def scheduled_generation():
    """Tarea programada que se ejecuta cada día a las 23:20."""
    global generation_running
    if generation_running:
        logger.warning("Ya hay una generación en curso, saltando esta ejecución.")
        return

    generation_running = True
    logger.info(f"🕐 Generación programada iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_episode_generation)
        if result["success"]:
            logger.info(f"✅ Episodio {result['episode_number']} publicado: {result['youtube_url']}")
        else:
            logger.error(f"❌ Error en generación: {result.get('error')}")
    except Exception as e:
        logger.error(f"Error en tarea programada: {e}", exc_info=True)
    finally:
        generation_running = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    Path("logs").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    Path("assets").mkdir(exist_ok=True)

    hour = int(os.getenv("SCHEDULE_HOUR", "23"))
    minute = int(os.getenv("SCHEDULE_MINUTE", "20"))

    scheduler.add_job(
        scheduled_generation,
        CronTrigger(hour=hour, minute=minute),
        id="daily_podcast",
        name=f"Generar episodio diario a las {hour:02d}:{minute:02d}",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info(f"⏰ Scheduler iniciado - próxima ejecución: {hour:02d}:{minute:02d} diario")

    yield

    scheduler.shutdown()
    logger.info("Scheduler detenido.")


# ── App FastAPI ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Podcast Automático - Personajes Famosos Vegetarianos del Mundo",
    description="Sistema automatizado para generar y publicar episodios del podcast en YouTube",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Rutas ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Sirve el dashboard principal."""
    return FileResponse("static/index.html")


@app.get("/api/status")
async def get_status():
    """Estado actual del sistema y próxima ejecución programada."""
    next_run = None
    job = scheduler.get_job("daily_podcast")
    if job and job.next_run_time:
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")

    hour = int(os.getenv("SCHEDULE_HOUR", "23"))
    minute = int(os.getenv("SCHEDULE_MINUTE", "20"))

    return {
        "scheduler_running": scheduler.running,
        "generation_running": generation_running,
        "next_scheduled_run": next_run,
        "schedule_time": f"{hour:02d}:{minute:02d}",
        "youtube_auth": check_youtube_auth(),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "tts_voice": os.getenv("TTS_VOICE", "onyx"),
        "tts_engine": "OpenAI TTS",
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/episodes")
async def get_episodes():
    """Lista todos los episodios generados."""
    episodes = get_all_episodes()
    return [
        {
            "id": ep.id,
            "episode_number": ep.episode_number,
            "character_name": ep.character_name,
            "character_nationality": ep.character_nationality,
            "character_profession": ep.character_profession,
            "status": ep.status,
            "youtube_url": ep.youtube_url,
            "youtube_video_id": ep.youtube_video_id,
            "created_at": ep.created_at.isoformat() if ep.created_at else None,
            "published_at": ep.published_at.isoformat() if ep.published_at else None,
            "error_message": ep.error_message,
        }
        for ep in episodes
    ]


@app.get("/api/episodes/{episode_id}")
async def get_episode_detail(episode_id: int):
    """Detalle de un episodio específico, incluyendo el guión."""
    ep = get_episode(episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    return {
        "id": ep.id,
        "episode_number": ep.episode_number,
        "character_name": ep.character_name,
        "character_nationality": ep.character_nationality,
        "character_profession": ep.character_profession,
        "script": ep.script,
        "audio_path": ep.audio_path,
        "video_path": ep.video_path,
        "thumbnail_path": ep.thumbnail_path,
        "youtube_url": ep.youtube_url,
        "youtube_video_id": ep.youtube_video_id,
        "status": ep.status,
        "error_message": ep.error_message,
        "created_at": ep.created_at.isoformat() if ep.created_at else None,
        "published_at": ep.published_at.isoformat() if ep.published_at else None,
    }


@app.post("/api/generate")
async def trigger_generation(background_tasks: BackgroundTasks):
    """Dispara manualmente la generación de un nuevo episodio."""
    global generation_running
    if generation_running:
        raise HTTPException(status_code=409, detail="Ya hay una generación en curso")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY no configurada")

    async def run_in_background():
        global generation_running
        generation_running = True
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, run_episode_generation)
        finally:
            generation_running = False

    background_tasks.add_task(run_in_background)

    return {"message": "Generación iniciada en segundo plano", "status": "running"}


@app.get("/api/channel")
async def get_channel():
    """Información del canal de YouTube conectado."""
    if not check_youtube_auth():
        return {"connected": False, "message": "YouTube no autenticado"}
    try:
        info = get_channel_info()
        return {"connected": True, **info}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/api/voices")
async def get_voices():
    """Lista las voces disponibles en OpenAI TTS."""
    openai_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    current = os.getenv("TTS_VOICE", "onyx")
    return {"current_voice": current, "voices": openai_voices}


@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """Últimas líneas del log del sistema."""
    log_file = Path("logs/podcast.log")
    if not log_file.exists():
        return {"logs": []}
    with open(log_file) as f:
        all_lines = f.readlines()
    return {"logs": [l.rstrip() for l in all_lines[-lines:]]}


@app.get("/api/thumbnail/{episode_id}")
async def get_thumbnail(episode_id: int):
    """Sirve la miniatura de un episodio."""
    ep = get_episode(episode_id)
    if not ep or not ep.thumbnail_path or not Path(ep.thumbnail_path).exists():
        raise HTTPException(status_code=404, detail="Miniatura no encontrada")
    return FileResponse(ep.thumbnail_path, media_type="image/jpeg")


@app.get("/api/youtube-auth")
async def youtube_auth_start(request: Request):
    """Inicia el flujo OAuth de YouTube. Redirige al usuario a Google para autorizar."""
    from fastapi.responses import RedirectResponse
    redirect_uri = str(request.base_url) + "api/youtube-auth/callback"
    auth_url = start_oauth_flow(redirect_uri)
    return RedirectResponse(auth_url)


@app.get("/api/youtube-auth/callback")
async def youtube_auth_callback(request: Request, code: str = None, error: str = None):
    """Callback de OAuth. Google redirige aquí tras la autorización del usuario."""
    from fastapi.responses import HTMLResponse
    if error:
        return HTMLResponse(f"<h2>Error de autorización: {error}</h2>")
    if not code:
        return HTMLResponse("<h2>No se recibió código de autorización.</h2>")
    try:
        redirect_uri = str(request.base_url) + "api/youtube-auth/callback"
        finish_oauth_flow(code, redirect_uri)
        return HTMLResponse("""
            <html><body style="font-family:sans-serif;text-align:center;padding:50px">
            <h2>✅ YouTube autorizado correctamente</h2>
            <p>Ya puedes cerrar esta ventana y volver al dashboard.</p>
            <a href="/">Volver al dashboard</a>
            </body></html>
        """)
    except Exception as e:
        logger.error(f"Error en OAuth callback: {e}", exc_info=True)
        return HTMLResponse(f"<h2>Error: {e}</h2>")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000")))
    uvicorn.run("main:app", host=host, port=port, reload=False)
