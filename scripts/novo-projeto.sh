#!/usr/bin/env bash
# Cria a pasta de um vídeo novo em projects/<slug>/ (só as pastas).
# O estado (_CLAUDE/projeto.json) é criado pela /video-iniciar com ferramentas/util/estado.py --criar.
#
# Uso: ./scripts/novo-projeto.sh <slug>      ex.: ./scripts/novo-projeto.sh retrovisage-04
#      ./scripts/novo-projeto.sh --proximo [canal]  # mostra o próximo <canal>-NN livre (padrão: retrovisage)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLUG="${1:-}"

CANAL_PADRAO="retrovisage"

proximo() {
  local canal="${1:-$CANAL_PADRAO}" n=1
  while [[ -e "$ROOT/projects/$(printf '%s-%02d' "$canal" "$n")" ]]; do n=$((n + 1)); done
  printf '%s-%02d\n' "$canal" "$n"
}

if [[ -z "$SLUG" ]]; then
  echo "Uso: $0 <slug>   (próximo livre: $(proximo))"
  exit 1
fi
[[ "$SLUG" == "--proximo" ]] && { proximo "${2:-}"; exit 0; }

if [[ ! "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "ERRO: use só letras minúsculas, números e hífen (ex.: retrovisage-04)"
  exit 1
fi

DEST="$ROOT/projects/$SLUG"
if [[ -e "$DEST" ]]; then
  echo "ERRO: projects/$SLUG já existe"
  exit 1
fi

cp -r "$ROOT/projects/_templates/pastas" "$DEST"
find "$DEST" -name .gitkeep -delete

echo "✅ projects/$SLUG criado: Roteiro/ Narracao/ Imagens/ Musica/ _CLAUDE/"
echo "Próximo: /video-roteiro → /video-humanizar → /video-iniciar → /video-narrar"
