#!/usr/bin/env bash
set -e

echo "▶ Rendering Quarto..."

quarto render

if [ -f report_pdf.pdf ]; then
  mv -f report_pdf.pdf docs/report.pdf
fi

echo "▶ Git add..."
git add .

echo "▶ Git status:"
git status --short

if git diff --cached --quiet; then
  echo "Keine Änderungen."
  exit 0
fi

read -rp "Commit-Nachricht: " MSG

git commit -m "$MSG"

echo "▶ Push..."

git push

echo
echo "Fertig."
