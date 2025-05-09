from flask import Flask, render_template, jsonify
from openai import OpenAI
import os
import json
import random

app = Flask(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# SYSTEM_PROMPT aus .env
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Standard-Backup-Prompt, falls nicht gesetzt.")
CACHE_FILE = "message_cache.json"
TOGGLE_FILE = "toggle.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)

def load_toggle():
    if os.path.exists(TOGGLE_FILE):
        with open(TOGGLE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("next", "new")
    return "new"

def save_toggle(next_value):
    with open(TOGGLE_FILE, "w", encoding="utf-8") as f:
        json.dump({"next": next_value}, f)

def fetch_new_message(existing_messages):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Erzähle mir etwas über KI."}
            ],
            max_tokens=512
        )

        if response.choices and response.choices[0].message:
            message = response.choices[0].message.content.strip()

            if message not in existing_messages:
                existing_messages.append(message)
                save_cache(existing_messages)
                print(f"✅ Neue Nachricht gespeichert: {message}")
            else:
                print("⚠️ Doppelte Nachricht – API wird erneut aufgerufen.")
                return fetch_new_message(existing_messages)

            return message

        return "[Keine Antwort: Keine choices]"

    except Exception as e:
        return f"API-Fehler: {e}"

def get_ai_message():
    cache = load_cache()
    toggle = load_toggle()

    if toggle == "new":
        message = fetch_new_message(cache)
        save_toggle("old")
    else:
        if cache:
            message = random.choice(cache)
            print(f"🔁 Alte Nachricht ausgegeben: {message}")
        else:
            message = fetch_new_message(cache)
        save_toggle("new")

    return message

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/message")
def api_message():
    message = get_ai_message()
    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
