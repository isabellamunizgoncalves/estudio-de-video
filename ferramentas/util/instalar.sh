#!/usr/bin/env bash
# Prepara o ambiente Python do fluxo (versão leve, sem PyTorch).
# Uso: bash ferramentas/util/instalar.sh   (rodar em segundo plano; leva alguns minutos)
# Padrão: .venv-edicao/ na raiz do repo; outro lugar com VENV=/caminho bash ferramentas/util/instalar.sh
# Sem GPU aqui: transcrição com faster-whisper (CTranslate2, sem PyTorch).
set -euo pipefail
VENV="${VENV:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.venv-edicao}"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q \
  "faster-whisper" \
  "numpy" \
  "opencv-python-headless" \
  "scenedetect" \
  "soundfile" \
  "rembg[cpu]"
# Modelo de transcrição: baixado do Hugging Face na primeira vez e guardado em cache.
"$VENV/bin/python" - <<'EOF'
from faster_whisper import WhisperModel
WhisperModel("large-v3", device="cpu", compute_type="int8")
print("modelo ok")
from rembg import new_session
new_session("isnet-general-use")
print("recorte ok")
EOF
echo "ambiente pronto em $VENV"