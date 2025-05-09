from flask import Flask, render_template, jsonify
from openai import OpenAI
import os
import json
import random
import logging
from rapidfuzz import fuzz
from flask_compress import Compress

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)
Compress(app)

# ➤ Provider-Infos
PROVIDERS = [
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "model": "openai/gpt-4o"
    },
    {
        "name": "Together",
        "base_url": "https://api.together.xyz/v1",
        "api_key": os.getenv("TOGETHER_API_KEY"),
        "model": "togethercomputer/llama-3-70b-chat"
    },
    {
        "name": "DeepInfra",
        "base_url": "https://api.deepinfra.com/v1/openai",
        "api_key": os.getenv("DEEPINFRA_API_KEY"),
        "model": "meta-llama/Meta-Llama-3-70B-Instruct"
    }
]

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Standard-Backup-Prompt, falls nicht gesetzt.")
CACHE_FILE = os.getenv("CACHE_FILE", "message_cache.json")
LAST_FILE = os.getenv("LAST_FILE", "last_messages.json")
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "85"))
CACHE_PROBABILITY = float(os.getenv("CACHE_PROBABILITY", "0.6"))
LAST_LIMIT = int(os.getenv("LAST_LIMIT", "3"))

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def load_last_messages():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("last", [])
    return []

def save_last_messages(messages):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump({"last": messages[-LAST_LIMIT:]}, f, ensure_ascii=False)

def is_similar(new_message, existing_messages, threshold=FUZZY_THRESHOLD):
    for msg in existing_messages:
        similarity = fuzz.ratio(new_message, msg)
        logging.debug(f"Ähnlichkeitsvergleich: '{new_message}' vs. '{msg}' → {similarity}%")
        if similarity >= threshold:
            return True
    return False

def fetch_new_message(existing_messages):
    for provider in PROVIDERS:
        try:
            logging.info(f"🔍 Versuche Provider: {provider['name']}")
            client = OpenAI(
                base_url=provider["base_url"],
                api_key=provider["api_key"]
            )

            response = client.chat.completions.create(
                model=provider["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "Erzähle mir etwas über KI."}
                ],
                max_tokens=512
            )

            logging.info(f"📝 API-Rohantwort ({provider['name']}): {response}")

            if not response.choices:
                logging.warning(f"⚠️ {provider['name']} → keine gültigen choices → versuche nächsten Provider")
                continue

            message = response.choices[0].message.content.strip()

            if not is_similar(message, existing_messages):
                existing_messages.append(message)
                save_cache(existing_messages)
                logging.info(f"✅ Neue Nachricht von {provider['name']} gespeichert: {message}")
                return message
            else:
                logging.warning(f"⚠️ Ähnliche Nachricht bei {provider['name']} erkannt → versuche nächsten Provider")
                continue

        except Exception as e:
            logging.error(f"❌ Fehler bei {provider['name']}: {e}")
            continue

    # ➤ Fallback
    if existing_messages:
        fallback = random.choice(existing_messages)
        logging.info(f"🕑 Alle Provider fehlgeschlagen → Fallback aus Cache: {fallback}")
        return fallback + " (aus Archiv)"

    return "[Keine Antwort von irgendeinem Provider]"

def get_ai_message():
    cache = load_cache()
    last_messages = load_last_messages()

    if cache and random.random() < CACHE_PROBABILITY:
        choices = [m for m in cache if m not in last_messages]
        if not choices:
            choices = cache
            logging.warning("⚠️ Alle Nachrichten waren kürzlich – nehme zufällig aus allen")
        message = random.choice(choices)
        last_messages.append(message)
        if len(last_messages) > LAST_LIMIT:
            last_messages = last_messages[-LAST_LIMIT:]
        save_last_messages(last_messages)
        logging.info(f"🔁 Alte (nicht kürzlich genutzte) Nachricht ausgegeben: {message}")
    else:
        message = fetch_new_message(cache)
        last_messages.append(message)
        if len(last_messages) > LAST_LIMIT:
            last_messages = last_messages[-LAST_LIMIT:]
        save_last_messages(last_messages)

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
