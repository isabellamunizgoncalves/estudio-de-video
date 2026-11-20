#!/usr/bin/env bash
# Sincroniza perfil do projeto com perfis/ global
# Uso: ./scripts/sync-perfil.sh <projeto> [perfil]
# Cria symlinks em projects/<projeto>/perfil/ apontando para perfis/<perfil>/

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJETO="${1:-}"
PERFIL="${2:-retrovisage}"

if [[ -z "$PROJETO" ]]; then
  echo "Uso: $0 <projeto> [perfil]"
  echo "Ex: $0 retrovisage-01 retrovisage"
  exit 1
fi

PROJETO_DIR="$ROOT/projects/$PROJETO"
PERFIL_SRC="$ROOT/perfis/$PERFIL"
PERFIL_DEST="$PROJETO_DIR/perfil"

if [[ ! -d "$PROJETO_DIR" ]]; then
  echo "ERRO: Projeto '$PROJETO' não encontrado"
  exit 1
fi

if [[ ! -d "$PERFIL_SRC" ]]; then
  echo "ERRO: Perfil '$PERFIL' não encontrado em $PERFIL_SRC"
  exit 1
fi

echo "🔗 Sincronizando perfil '$PERFIL' → projeto '$PROJETO'"
rm -rf "$PERFIL_DEST"
ln -sfn "$PERFIL_SRC" "$PERFIL_DEST"

# Verificar
echo ""
echo "Conteúdo de $PERFIL_DEST:"
ls -la "$PERFIL_DEST"/

echo ""
echo "✅ Perfil sincronizado. O projeto agora usa perfis/$PERFIL/"
echo "   Para trocar de perfil: $0 $PROJETO novo-perfil"