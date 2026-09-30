import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory

from gemini_service import generate_comic, generate_panel_image

load_dotenv()

app = Flask(__name__)
GENERATED_DIR = Path("generated")
GENERATED_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/generate-story")
def generate_story():
    data = request.get_json(silent=True) or {}

    idea = (data.get("idea") or "").strip()
    genre = (data.get("genre") or "Adventure").strip()
    characters = (data.get("characters") or "").strip()
    panels = int(data.get("panels") or 4)

    if not idea:
        return jsonify({"error": "Please enter a story idea."}), 400

    panels = max(2, min(panels, 8))

    try:
        comic = generate_comic(
            idea=idea,
            genre=genre,
            characters=characters,
            panel_count=panels,
        )

        story_id = comic.get("title", "comic").lower().replace(" ", "_")
        story_file = GENERATED_DIR / f"{story_id}.json"
        story_file.write_text(
            json.dumps(comic, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return jsonify(comic)
    except Exception as exc:
        error_message = str(exc)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return jsonify({
                "error": "Image generation is currently unavailable on your API tier."
            }), 429

        return jsonify({"error": error_message}), 500


@app.post("/api/generate-image")
def generate_image():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    panel_number = int(data.get("panel_number") or 1)

    if not prompt:
        return jsonify({"error": "Image prompt is required."}), 400

    try:
        filename = generate_panel_image(prompt, panel_number, GENERATED_DIR)
        return jsonify({"image_url": f"/generated/{filename}"})
    except Exception as exc:
        error_message = str(exc)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return jsonify({
                "error": "Image generation is currently unavailable on your API tier."
            }), 429

        return jsonify({"error": error_message}), 500


@app.get("/generated/<path:filename>")
def generated_file(filename):
    return send_from_directory(GENERATED_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
