#!/bin/bash
# Install pets to their respective app directories
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

CODEX_PETS_DIR="${CODEX_HOME:-$HOME/.codex}/pets"
CLAWD_THEMES_DIR="$HOME/Library/Application Support/clawd-on-desk/themes"

echo "Installing pets..."

for pet_dir in "$SCRIPT_DIR"/*/; do
  pet_name="$(basename "$pet_dir")"
  [ "$pet_name" = ".git" ] && continue

  if [ -d "$pet_dir/codex" ]; then
    mkdir -p "$CODEX_PETS_DIR/$pet_name"
    cp "$pet_dir/codex/"* "$CODEX_PETS_DIR/$pet_name/"
    echo "  [Codex] $pet_name -> $CODEX_PETS_DIR/$pet_name/"
  fi

  if [ -d "$pet_dir/clawd-on-desk" ]; then
    mkdir -p "$CLAWD_THEMES_DIR/$pet_name"
    cp "$pet_dir/clawd-on-desk/theme.json" "$CLAWD_THEMES_DIR/$pet_name/"
    if [ -d "$pet_dir/clawd-on-desk/assets" ]; then
      cp -r "$pet_dir/clawd-on-desk/assets" "$CLAWD_THEMES_DIR/$pet_name/"
    fi
    echo "  [Clawd] $pet_name -> $CLAWD_THEMES_DIR/$pet_name/"
  fi
done

echo "Done! Restart Codex / Clawd on Desk to see your pets."
