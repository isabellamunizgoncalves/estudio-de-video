#!/usr/bin/env bash
# Prepara o ambiente Python local (dentro do repo)
# Uso: bash scripts/instalar-local.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$REPO_DIR/.venv-edicao"

echo "=== Instalando ambiente em $VENV ==="

if [ ! -x "$VENV/bin/python" ]; then
  echo "Criando venv..."
  python3 -m venv "$VENV"
fi

echo "Atualizando pip..."
"$VENV/bin/pip" install -q --upgrade pip

echo "Instalando pacotes..."
"$VENV/bin/pip" install -q \
  "faster-whisper" \
  "numpy" \
  "opencv-python-headless" \
  "scenedetect" \
  "soundfile" \
  "rembg[cpu]"

echo "Baixando modelos (primeira vez demora)..."
"$VENV/bin/python" << 'EOF'
from faster_whisper import WhisperModel
print("Carregando Whisper large-v3 (CPU, int8)...")
WhisperModel("large-v3", device="cpu", compute_type="int8")
print("modelo ok")

from rembg import new_session
print("Carregando rembg isnet-general-use...")
new_session("isnet-general-use")
print("recorte ok")
EOF

echo "=== Ambiente pronto em $VENV ==="
echo "Python: $VENV/bin/python"