#!/bin/bash

# Skript zum Erstellen der Ordnerstruktur und Umgebung für ai-ticker

# Projektstruktur
mkdir -p static templates tests .github/workflows

# Virtuelle Umgebung erstellen
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# .env aus .env.example kopieren, wenn noch nicht vorhanden
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "✅ .env aus .env.example erstellt. Bitte API-Keys eintragen!"
else
  echo "⚠️ .env existiert bereits oder .env.example fehlt."
fi

echo "✅ Projektumgebung erfolgreich eingerichtet!"
echo "🚀 Starte die App mit 'python app.py'"
