"""
Script de configuración inicial del podcast automático.
Ejecutar una vez para verificar dependencias y generar la portada.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python():
    if sys.version_info < (3, 11):
        print("❌ Se requiere Python 3.11 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")


def check_ffmpeg():
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode == 0:
        print("✅ FFmpeg instalado")
    else:
        print("❌ FFmpeg no encontrado. Instálalo:")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
        sys.exit(1)


def check_env():
    env_file = Path(".env")
    if not env_file.exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("📋 Archivo .env creado desde .env.example")
            print("   ⚠️  EDITA el archivo .env con tus claves API antes de continuar")
        else:
            print("❌ No se encontró .env.example")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    missing = []
    if not os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") == "tu_clave_anthropic_aqui":
        missing.append("ANTHROPIC_API_KEY")
    if not os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY") == "tu_clave_elevenlabs_aqui":
        missing.append("ELEVENLABS_API_KEY")

    if missing:
        print(f"⚠️  Variables no configuradas en .env: {', '.join(missing)}")
        return False

    print("✅ Variables de entorno configuradas")
    return True


def create_directories():
    dirs = ["output", "logs", "assets", "credentials", "static"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Directorios creados")


def generate_podcast_cover():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from thumbnail_generator import create_podcast_cover
        cover_path = create_podcast_cover()
        print(f"✅ Portada del podcast creada: {cover_path}")
    except Exception as e:
        print(f"⚠️  No se pudo crear la portada: {e}")


def print_next_steps():
    print("\n" + "=" * 60)
    print("🌿 CONFIGURACIÓN INICIAL COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print()
    print("1. CLAVES API - Edita el archivo .env con:")
    print("   • ANTHROPIC_API_KEY  → https://console.anthropic.com")
    print("   • ELEVENLABS_API_KEY → https://elevenlabs.io")
    print()
    print("2. YOUTUBE - Configura las credenciales OAuth2:")
    print("   a. Ve a https://console.cloud.google.com")
    print("   b. Crea un proyecto nuevo")
    print("   c. Activa 'YouTube Data API v3'")
    print("   d. Crea credenciales OAuth 2.0 (tipo: App de escritorio)")
    print("   e. Descarga el JSON y guárdalo como: credentials/client_secret.json")
    print("   f. En la primera ejecución se abrirá el navegador para autorizar")
    print()
    print("3. INICIAR el servidor:")
    print("   python main.py")
    print("   o: uvicorn main:app --host 0.0.0.0 --port 8000")
    print()
    print("4. PANEL WEB: http://localhost:8000")
    print()
    print("📅 Episodios se generan automáticamente cada día a las 23:20h")
    print("   (configurable en .env con SCHEDULE_HOUR y SCHEDULE_MINUTE)")
    print()
    print("=" * 60)


if __name__ == "__main__":
    print("\n🌿 Configuración inicial - Podcast Vegetariano Automático\n")
    check_python()
    check_ffmpeg()
    create_directories()
    env_ok = check_env()
    if env_ok:
        generate_podcast_cover()
    print_next_steps()
