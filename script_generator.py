"""
Generador de guiones usando la API de Claude.
Crea episodios detallados sobre personajes famosos vegetarianos del mundo.
"""

import os
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Lista de personajes famosos vegetarianos del mundo para sugerir a Claude
SEED_CHARACTERS = [
    "Leonardo da Vinci", "Mahatma Gandhi", "Albert Einstein", "Leo Tolstói",
    "Nikola Tesla", "Paul McCartney", "Natalie Portman", "Brad Pitt",
    "Serena Williams", "Mike Tyson", "Lewis Hamilton", "Novak Djokovic",
    "Venus Williams", "Carl Lewis", "Scott Jurek", "Rich Roll",
    "Ellen DeGeneres", "Joaquin Phoenix", "Woody Harrelson", "Moby",
    "Pythagoras", "Voltaire", "Benjamin Franklin", "Henry David Thoreau",
    "George Bernard Shaw", "Franz Kafka", "Albert Schweitzer",
    "Charles Darwin", "Isaac Newton", "Plutarco",
    "Anne Hathaway", "Alicia Silverstone", "Miley Cyrus", "Ariana Grande",
    "Billie Eilish", "Pamela Anderson", "Tobey Maguire", "Jared Leto",
    "Peter Singer", "Jane Goodall", "Carl Sagan", "Russell Brand",
    "Dennis Rodman", "Mac Danzig", "Nate Diaz", "David Carter",
    "Fiona Oakes", "Patrik Baboumian", "Torre Washington",
]


def select_character(used_characters: list[str]) -> dict:
    """Usa Claude para seleccionar el siguiente personaje vegetariano."""
    used_list = "\n".join(f"- {c}" for c in used_characters) if used_characters else "Ninguno aún."
    seed_list = "\n".join(f"- {c}" for c in SEED_CHARACTERS)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""Eres el productor del podcast "Personajes Famosos Vegetarianos del Mundo".

Personajes ya usados en episodios anteriores:
{used_list}

Lista de referencia de personajes vegetarianos conocidos (puedes elegir uno de aquí o proponer otro):
{seed_list}

Selecciona UN personaje famoso vegetariano o vegano que NO haya sido usado aún.
Puede ser de cualquier época, país o profesión: artistas, científicos, deportistas, filósofos, activistas, etc.

Responde ÚNICAMENTE con este JSON exacto (sin markdown, sin explicaciones):
{{
  "nombre": "Nombre Completo del Personaje",
  "nacionalidad": "País de origen",
  "profesion": "Profesión o campo principal",
  "anos_vida": "Año nacimiento - Año muerte (o 'Nacido en XXXX' si vive)",
  "razon_vegetariano": "Breve razón de su vegetarianismo"
}}""",
            }
        ],
    )

    import json
    text = response.content[0].text.strip()
    # Limpiar posibles bloques de código markdown
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def generate_script(character_info: dict, episode_number: int) -> str:
    """Genera el guión completo del episodio con Claude."""
    nombre = character_info["nombre"]
    nacionalidad = character_info["nacionalidad"]
    profesion = character_info["profesion"]
    anos = character_info.get("anos_vida", "")
    razon = character_info.get("razon_vegetariano", "")

    prompt = f"""Eres el guionista y conductor del podcast "Personajes Famosos Vegetarianos del Mundo".
Este es el episodio número {episode_number}.

El personaje de este episodio es:
- Nombre: {nombre}
- Nacionalidad: {nacionalidad}
- Profesión: {profesion}
- Años de vida: {anos}
- Relación con el vegetarianismo: {razon}

Escribe un guión de podcast completo en ESPAÑOL, atractivo y educativo, de aproximadamente 8-12 minutos de duración (entre 1200 y 1800 palabras).

El guión debe seguir esta estructura:
1. **INTRO** (30 seg): Música de fondo imaginaria, bienvenida entusiasta al podcast
2. **PRESENTACIÓN DEL EPISODIO** (1 min): Anuncio del personaje con suspenso y curiosidad
3. **HISTORIA DE VIDA** (3-4 min): Biografía fascinante, infancia, logros principales, contexto histórico
4. **SU VEGETARIANISMO** (2-3 min): Cuándo y por qué adoptó esta dieta, cómo influyó en su vida y obra
5. **LEGADO E IMPACTO** (1-2 min): Su influencia en el mundo vegetariano y en general
6. **REFLEXIÓN FINAL** (1 min): Lección o inspiración que dejamos al oyente
7. **CIERRE** (30 seg): Despedida, invitación a suscribirse y anuncio del próximo episodio

IMPORTANTE:
- Escribe SOLO el texto que se leerá en voz alta (sin acotaciones de escena, sin [música], sin [pausa])
- Usa un tono conversacional, cálido y apasionado
- Incluye datos curiosos y poco conocidos
- Conecta el vegetarianismo con su filosofía de vida
- El conductor se llama "Alejandro" y habla en primera persona
- Termina con "Hasta el próximo episodio de Personajes Famosos Vegetarianos del Mundo"

Escribe el guión completo ahora:"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()


def generate_title_and_description(character_info: dict, episode_number: int, script: str) -> dict:
    """Genera título, descripción y tags optimizados para YouTube."""
    nombre = character_info["nombre"]

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": f"""Crea metadatos optimizados para YouTube del episodio {episode_number} del podcast "Personajes Famosos Vegetarianos del Mundo" sobre {nombre}.

Primeras 200 palabras del guión:
{script[:800]}

Responde ÚNICAMENTE con este JSON (sin markdown):
{{
  "titulo": "Título atractivo para YouTube (máx 100 caracteres, incluye el nombre, episodio y algo llamativo)",
  "descripcion": "Descripción completa para YouTube (300-500 palabras) con introducción al personaje, qué aprenderán, timestamps sugeridos, hashtags y llamada a la acción para suscribirse",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"]
}}""",
            }
        ],
    )

    import json
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
