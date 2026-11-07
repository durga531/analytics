#!/usr/bin/env bash
# Second-brain installer wrapper (macOS first; Linux works too).
# Usage: bash install.sh "<path to your Obsidian vault>" [--dry-run] [--yes] [--name NAME] [--no-mcp] [--no-autostart]
# Non-destructive: see install.py for the guarantees.
set -eu
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -lt 1 ]; then
  echo "usage: bash install.sh \"<path to your Obsidian vault>\" [--dry-run] [--yes] [--name NAME]" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. On macOS run: xcode-select --install   (or: brew install python)" >&2
  exit 1
fi
exec python3 "$KIT_DIR/install.py" "$@"
