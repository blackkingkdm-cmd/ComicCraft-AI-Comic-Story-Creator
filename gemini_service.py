import base64
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.5-flash-lite")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

client = genai.Client(api_key=api_key)


def _extract_json(text: str) -> dict:
    text = text.strip()

    # Remove Markdown code fences if Gemini adds them.
    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Gemini did not return valid JSON.")
        return json.loads(text[start:end + 1])


def generate_comic(idea, genre, characters, panel_count):
    character_text = characters or "Create suitable original characters."

    prompt = f"""
You are ComicCraft, an AI comic story creator.

Create a short, original comic story from the user's idea.

User idea:
{idea}

Genre:
{genre}

Characters:
{character_text}

Number of comic panels:
{panel_count}

Return ONLY valid JSON in exactly this structure:
{{
  "title": "short comic title",
  "logline": "one sentence summary",
  "characters": [
    {{
      "name": "character name",
      "description": "visual and personality description"
    }}
  ],
  "panels": [
    {{
      "panel": 1,
      "scene": "what is visually happening",
      "dialogue": [
        {{"speaker": "name", "text": "short dialogue"}}
      ],
      "caption": "optional narration",
      "image_prompt": "detailed prompt for generating this comic panel"
    }}
  ]
}}

Rules:
- Keep the story family-friendly.
- Make every panel continue naturally from the previous panel.
- Keep dialogue short enough for a comic speech bubble.
- Make character appearance descriptions consistent across panels.
- Do not use copyrighted characters or existing franchises.
- The image_prompt must describe the scene, characters, expressions, camera angle,
  environment, lighting and comic-art style.
"""

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    comic = _extract_json(response.text)

    if "panels" not in comic:
        raise ValueError("Gemini response does not contain panels.")

    return comic


def generate_panel_image(prompt: str, panel_number: int, output_dir: Path) -> str:
    full_prompt = f"""
Create a single comic-book panel for ComicCraft.

{prompt}

Requirements:
- Original characters only.
- Family-friendly.
- Strong visual storytelling.
- Clean comic illustration.
- Keep the composition suitable for a single rectangular panel.
- Do not imitate a specific living artist.
"""

    # Current Gemini image-generation API.
    interaction = client.interactions.create(
        model=IMAGE_MODEL,
        input=full_prompt,
        response_format={
            "type": "image",
            "aspect_ratio": "16:9",
            "image_size": "1K",
        },
    )

    image_data = getattr(interaction, "output_image", None)
    if image_data is None:
        raise ValueError("Gemini did not return an image.")

    raw = base64.b64decode(image_data.data)
    filename = f"panel_{panel_number}.png"
    (output_dir / filename).write_bytes(raw)
    return filename
