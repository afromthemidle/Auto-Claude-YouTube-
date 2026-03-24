# 🌿 Podcast Automático: Personajes Famosos Vegetarianos del Mundo

Sistema completo que genera y publica automáticamente episodios diarios de un podcast en YouTube, con voz ultra-realista en español generada por IA.

## ¿Cómo funciona?

Cada día a las **23:20h** el sistema ejecuta automáticamente este pipeline:

```
Claude AI            ElevenLabs          FFmpeg             YouTube
(Guión) ──────────→ (Voz realista) ────→ (Video HD) ──────→ (Publicar)
   ↓                     ↓                   ↓
Selecciona un        Convierte texto      Combina imagen
personaje nuevo      a audio MP3          + audio → MP4
vegetariano          con voz española     con visualizador
famoso               muy realista         de audio animado
```

## Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Guión / IA | Claude Haiku (Anthropic) |
| Voz realista | edge-tts - Microsoft Neural (gratuito) |
| Video | FFmpeg (1920×1080 Full HD) |
| Thumbnails | Pillow (Python) |
| Publicación | YouTube Data API v3 |
| Backend | FastAPI + APScheduler |
| Base de datos | SQLite |

## Instalación rápida

### Requisitos previos

- Python 3.11+
- FFmpeg instalado en el sistema
- Cuentas en Anthropic, ElevenLabs y Google Cloud

### 1. Clonar e instalar dependencias

```bash
git clone <repositorio>
cd Auto-Claude-YouTube-

pip install -r requirements.txt
```

### 2. Configuración inicial

```bash
python setup.py
```

Esto crea el archivo `.env` y verifica dependencias.

### 3. Configurar claves API

Edita el archivo `.env`:

```env
# Claude AI (guión del podcast)
ANTHROPIC_API_KEY=tu_clave_aqui   # https://console.anthropic.com

# ElevenLabs (voz realista en español)
ELEVENLABS_API_KEY=tu_clave_aqui  # https://elevenlabs.io
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB  # Puedes cambiar la voz

# Horario de publicación
SCHEDULE_HOUR=23
SCHEDULE_MINUTE=20
```

### 4. Configurar YouTube (OAuth2)

1. Entra a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto nuevo
3. Activa **YouTube Data API v3** (APIs y servicios → Biblioteca)
4. Ve a **Credenciales → Crear credenciales → ID de cliente OAuth 2.0**
5. Tipo de aplicación: **Aplicación de escritorio**
6. Descarga el JSON y guárdalo como: `credentials/client_secret.json`
7. La primera vez que generes un episodio, se abrirá el navegador para que autorices el acceso a tu canal

### 5. Iniciar el servidor

```bash
python main.py
```

Accede al panel web en: **http://localhost:8000**

## Panel de Control Web

El dashboard web permite:

- 📊 **Ver estado** del sistema (APIs configuradas, próxima ejecución)
- ▶️ **Generar episodios manualmente** sin esperar al horario
- 📚 **Ver todos los episodios** con enlaces a YouTube
- 📄 **Leer el guión** de cada episodio
- 📋 **Ver logs** del sistema en tiempo real

## Estructura del proyecto

```
├── main.py                  # Servidor FastAPI + Scheduler APScheduler
├── podcast_generator.py     # Pipeline principal de generación
├── script_generator.py      # Guión con Claude AI
├── tts_generator.py         # Audio con ElevenLabs TTS
├── video_creator.py         # Video con FFmpeg
├── thumbnail_generator.py   # Miniaturas con Pillow
├── youtube_uploader.py      # Publicación en YouTube API v3
├── database.py              # Base de datos SQLite
├── setup.py                 # Script de configuración inicial
├── static/
│   └── index.html           # Dashboard web
├── output/                  # Episodios generados (audio, video, imagen)
├── credentials/             # Credenciales de YouTube (NO subir a git)
├── logs/                    # Logs del sistema
├── .env                     # Variables de entorno (NO subir a git)
├── .env.example             # Plantilla de configuración
└── requirements.txt         # Dependencias Python
```

## Personalización

### Cambiar la voz

Edita `TTS_VOICE` en `.env`. Todas las voces son gratuitas:

```env
TTS_VOICE=es-ES-AlvaroNeural    # España, masculino  ← por defecto
TTS_VOICE=es-MX-JorgeNeural     # México, masculino
TTS_VOICE=es-AR-TomasNeural     # Argentina, masculino
TTS_VOICE=es-ES-ElviraNeural    # España, femenino
TTS_VOICE=es-MX-DaliaNeural     # México, femenino
```

Ver todas las voces disponibles: `GET /api/voices`

### Cambiar el horario

```env
SCHEDULE_HOUR=23    # Hora (0-23)
SCHEDULE_MINUTE=20  # Minuto (0-59)
```

### Privacidad del video en YouTube

```env
YOUTUBE_PRIVACY=public    # public / unlisted / private
```

### Añadir personajes a la lista de sugerencias

Edita `SEED_CHARACTERS` en `script_generator.py`.

## Variables de entorno completas

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `ANTHROPIC_API_KEY` | Clave de Anthropic (Claude) | — |
| `TTS_VOICE` | Voz de edge-tts (gratuito) | `es-ES-AlvaroNeural` |
| `TTS_RATE` | Velocidad de habla | `-5%` |
| `TTS_VOLUME` | Volumen del audio | `+10%` |
| `YOUTUBE_CLIENT_SECRETS_FILE` | Ruta al JSON de credenciales | `credentials/client_secret.json` |
| `YOUTUBE_TOKEN_FILE` | Ruta al token OAuth guardado | `credentials/youtube_token.json` |
| `YOUTUBE_CATEGORY_ID` | Categoría YouTube (22=Personas) | `22` |
| `YOUTUBE_PRIVACY` | Privacidad del video | `public` |
| `SCHEDULE_HOUR` | Hora de generación diaria | `23` |
| `SCHEDULE_MINUTE` | Minuto de generación diaria | `20` |
| `SERVER_HOST` | Host del servidor | `0.0.0.0` |
| `SERVER_PORT` | Puerto del servidor | `8000` |

## Costos estimados por episodio

| Servicio | Uso estimado | Costo aprox. |
|----------|-------------|-------------|
| Claude Haiku | ~5000 tokens | ~$0.003 |
| edge-tts (Microsoft) | ilimitado | **GRATIS** |
| YouTube API | 1 subida | **GRATIS** |
| **Total** | | **~$0.003/episodio** |

> **Practicamente gratuito.** Con $1 puedes generar más de 300 episodios.

## Seguridad

- El archivo `.env` y la carpeta `credentials/` están en `.gitignore`
- **Nunca subas** tus claves API o el `client_secret.json` a GitHub
- Los tokens de YouTube se renuevan automáticamente

## Licencia

MIT
