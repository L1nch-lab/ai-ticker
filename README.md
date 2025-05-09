# AI-Ticker 🦾📰

**AI-Ticker** ist eine minimalistische Webanwendung, die regelmäßig interessante, kurze Fakten oder witzige Aussagen über künstliche Intelligenz präsentiert – perfekt für den Einsatz auf Infodisplays oder als Dashboard-Element in Unternehmen.

Die App ruft KI-generierte Nachrichten über OpenAI oder OpenRouter APIs ab und zeigt sie automatisch in einem ansprechenden, professionellen Design mit animiertem Roboter-Avatar an.

---

## 📸 **Features**

✅ Anzeige zufällig generierter, kurzer KI-Fakten  
✅ Ausgabe als Sprechblase mit animiertem Roboter  
✅ Automatisches Abrufen neuer Nachrichten alle 30 Sekunden  
✅ Speicherung bereits abgerufener Nachrichten (zur Wiederverwendung, Token-Sparen)  
✅ Konfigurierbar via `.env`  
✅ Deployment-ready via **Docker Compose**

---

## 🚀 **Setup & Installation**

### 📝 **1️⃣ .env-Datei anlegen**

Das Projekt verwendet eine `.env`-Datei für alle vertraulichen Konfigurationen.

👉 Kopiere die Beispiel-Datei:

```bash
cp .env.example .env

👉 Öffne die .env in einem Editor und trage deine Daten ein:

# OpenAI oder OpenRouter API-Key
OPENAI_API_KEY=dein-openai-api-key
OPENROUTER_API_KEY=dein-openrouter-api-key

# Der System-Prompt (wie die KI antworten soll)
SYSTEM_PROMPT="Du bist ein humorvoller, neugieriger KI-Experte, der kurze, interessante Fakten erzählt. Auf Deutsch. Max. 20 Wörter."

👉 Baue & starte die App:

docker compose up --build


Die Anwendung ist jetzt erreichbar unter:

➡️ http://localhost:5000