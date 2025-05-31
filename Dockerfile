FROM python:3.11-slim

# Erstelle nicht-root Benutzer für mehr Sicherheit
RUN groupadd -r aiticker && useradd -r -g aiticker aiticker

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_RUN_HOST=0.0.0.0

# Setze Rechte und wechsle zum nicht-root Benutzer
RUN chown -R aiticker:aiticker /app
USER aiticker

# Starte mit Gunicorn für Produktion
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers=2", "--threads=2", "app:app"]