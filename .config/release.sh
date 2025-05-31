#!/bin/bash

# Erstelle eine neue Projektversion
VERSION=$(date +%Y.%m.%d)
echo "Erstelle Version $VERSION"

# Änderungen committen, wenn es welche gibt
git diff --quiet || {
  echo "Uncommittete Änderungen gefunden. Committe mit Standardnachricht..."
  git add .
  git commit -m "Version $VERSION - $(date)"
}

# Neue Version taggen
git tag -a "v$VERSION" -m "Version $VERSION"

# Auf GitHub pushen (falls gewünscht)
read -p "Auf GitHub pushen? (j/n): " PUSH
if [ "$PUSH" = "j" ]; then
  git push origin main
  git push origin "v$VERSION"
  echo "✅ Version $VERSION gepusht"
else
  echo "❌ Push abgebrochen"
fi

echo "Fertig! Version $VERSION erstellt."
