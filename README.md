# ComicCraft – AI Comic Story Creator

ComicCraft is a Flask web application that uses Google Gemini models to turn a user's idea into an original comic story.

## Features

- Generate a complete comic storyline
- Generate characters and descriptions
- Generate scene-by-scene dialogue
- Generate image prompts for each panel
- Generate comic panel images with Gemini image generation
- Download the generated story as a TXT file

## Project structure

```text
ComicCraft/
│
├── app.py
├── gemini_service.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   ├── app.js
│   └── style.css
│
└── generated/
```

## 1. Install Python

Use Python 3.10+.

Check:

```bash
python --version
```

## 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install packages

```bash
pip install -r requirements.txt
```

## 4. Create a Gemini API key

Create an API key in Google AI Studio and keep it private.

Then copy `.env.example` to `.env` and put your key there:

```text
GEMINI_API_KEY=YOUR_KEY
```

## 5. Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## How the application works

```text
User idea
   ↓
Flask frontend
   ↓
Python backend
   ↓
Gemini text model
   ↓
Story + Characters + Panels + Dialogue
   ↓
Gemini image model
   ↓
Comic panel images
   ↓
Final Comic
```

## Important

Never put your Gemini API key directly inside HTML or JavaScript. Keep it in `.env`.

If a particular Gemini model is unavailable for your API key/project, change the model names in `.env` to models currently available to you.
