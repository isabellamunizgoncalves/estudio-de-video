#!/usr/bin/env bash
# Liga (symlink) as skills deste repo no diretório de skills do Claude Code / OpenCode.
# Fonte única: skills/<skill>/SKILL.md  →  <destino>/<skill>
#
# Uso:
#   ./scripts/skill-install.sh                 # instala todas em ~/.claude/skills
#   ./scripts/skill-install.sh video-mapa video  # só as escolhidas
#   ./scripts/skill-install.sh --target ~/.config/opencode/skills
#   ./scripts/skill-install.sh --list
#   ./scripts/skill-install.sh --repo          # liga em .claude/skills/ deste repo (links relativos, versionados)
#
# Se já existir uma pasta comum (não-symlink) com o mesmo nome no destino,
# ela é movida para _arquivo/skills-instaladas-antigas/ antes de criar o link.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$HOME/.claude/skills"
BACKUP_DIR="$ROOT/_arquivo/skills-instaladas-antigas"
LIST_ONLY=false
WANTED=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --target) TARGET_DIR="$2"; shift 2 ;;
    --list)   LIST_ONLY=true; shift ;;
    --repo)   TARGET_DIR="$ROOT/.claude/skills"; shift ;;
    -h|--help) sed -n 2,13p "$0"; exit 0 ;;
    *) WANTED+=("$1"); shift ;;
  esac
done

# Descobre todas as skills: skills/<skill>/SKILL.md
declare -A SRC
while IFS= read -r f; do
  d="$(dirname "$f")"
  SRC["$(basename "$d")"]="$d"
done < <(find "$ROOT/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | sort)

if $LIST_ONLY; then
  for name in $(printf '%s\n' "${!SRC[@]}" | sort); do
    printf '%s\n' "$name"
  done
  exit 0
fi

[[ ${#WANTED[@]} -eq 0 ]] && WANTED=("${!SRC[@]}")
mkdir -p "$TARGET_DIR"

for name in "${WANTED[@]}"; do
  src="${SRC[$name]:-}"
  if [[ -z "$src" ]]; then
    echo "❌ skill '$name' não encontrada (use --list)"; continue
  fi
  dest="$TARGET_DIR/$name"
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    mkdir -p "$BACKUP_DIR"
    mv "$dest" "$BACKUP_DIR/$name.$(date +%Y%m%d-%H%M%S)"
    echo "↪  cópia antiga de $name guardada em _arquivo/skills-instaladas-antigas/"
  fi
  if [[ "$TARGET_DIR" == "$ROOT"/* ]]; then
    ln -sfn --relative "$src" "$dest"   # dentro do repo: link relativo, funciona em qualquer máquina
  else
    ln -sfn "$src" "$dest"
  fi
  echo "✅ $name → ${src#$ROOT/}"
done
