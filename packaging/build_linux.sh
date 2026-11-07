#!/usr/bin/env bash
# Build a Linux onedir bundle of RetailPOS with PyInstaller.
# Run from anywhere; paths below are relative to the repo root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if [ ! -d venv ]; then
    echo "No venv/ found in $REPO_ROOT - create one and 'pip install -r requirements.txt' first." >&2
    exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate

python -c "import PyInstaller" 2>/dev/null || pip install pyinstaller

rm -rf build dist

pyinstaller packaging/RetailPOS.spec --noconfirm

echo
echo "Build complete: $REPO_ROOT/dist/RetailPOS/"
echo "Run it with: $REPO_ROOT/dist/RetailPOS/RetailPOS"
