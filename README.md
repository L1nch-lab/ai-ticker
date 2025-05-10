# AI-Ticker Dashboard

🧠 Ein einfaches Flask-Dashboard, das KI-generierte Nachrichten in einer Sprechblase anzeigt, inkl. Fallback-Cache und mehreren API-Providern.

## 🚀 Features

✅ Flask-Webserver mit `/api/message`-Endpoint  
✅ OpenAI-kompatible APIs: OpenRouter, Together, DeepInfra (Fallbacks integriert)  
✅ Nachrichten-Cache mit Ähnlichkeitsprüfung (RapidFuzz)  
✅ Frontend mit Robotersprechblase (HTML/CSS)  
✅ Docker-Container inklusive  
✅ `.env`-Konfiguration

---

## 🖥️ **Lokale Entwicklung**

1️⃣ Repository klonen:

```bash
git clone https://github.com/deinusername/ai-ticker.git
cd ai-ticker
2️⃣ Virtualenv aktivieren:

bash
Kopieren
Bearbeiten
python3 -m venv .venv
source .venv/bin/activate
3️⃣ Abhängigkeiten installieren:

bash
Kopieren
Bearbeiten
pip install -r requirements.txt
4️⃣ .env erstellen:

bash
Kopieren
Bearbeiten
cp .env.example .env
→ Fülle deine API-Keys in .env aus (siehe unten)

5️⃣ Starten:

bash
Kopieren
Bearbeiten
python app.py
🐳 Docker
Bauen & starten:

bash
Kopieren
Bearbeiten
docker compose up --build
→ Zugriff unter http://localhost:5000

⚙️ .env Konfiguration
Beispiel:

env
Kopieren
Bearbeiten
OPENROUTER_API_KEY=your-openrouter-key
TOGETHER_API_KEY=your-together-key
DEEPINFRA_API_KEY=your-deepinfra-key

SYSTEM_PROMPT=Du bist ein hilfreicher Assistent.
CACHE_FILE=message_cache.json
LAST_FILE=last_messages.json
FUZZY_THRESHOLD=85
CACHE_PROBABILITY=0.6
LAST_LIMIT=3
📡 Provider Info
OpenRouter: https://openrouter.ai

Together: https://api.together.ai/models

DeepInfra: https://deepinfra.com

Die App wechselt automatisch zum nächsten Provider, falls einer fehlschlägt.

