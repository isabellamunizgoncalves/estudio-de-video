#!/usr/bin/env bash
# Wrapper unificado para rodar etapas do fluxo Rétrovisage
# Uso: ./scripts/video.sh <projeto> <etapa> [args...]
#
# Etapas: iniciar | preparar | mapa | imagens | animar | som | final | status
#         alinhar | pausas | conferir | mixar | render | recortar | nova-cena

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJETO="${1:-}"
ETAPA="${2:-}"
shift 2 || true
ARGS=("$@")

if [[ -z "$PROJETO" || -z "$ETAPA" ]]; then
  cat << 'USAGE'
Uso: rv.sh <projeto> <etapa> [args...]

Etapas do fluxo principal:
  iniciar     - Abre o vídeo: estado, briefing e capítulos (/video-iniciar)
  preparar    - Alinha a narração de Narracao/ com o roteiro e ajusta pausas (/video-preparar)
  mapa        - Plano cena a cena (/video-mapa)
  imagens     - Busca e recorta imagens (/video-imagens)
  animar      - Anima e renderiza rascunho 720p (/video-animar)
  som         - Música e efeitos sob a voz (/video-som)
  final       - Vídeo final 1080p, -14 LUFS (/video-final)

Ferramentas individuais:
  alinhar     - Alinha narração com roteiro (WhisperX)
  pausas      - Encurta pausas longas na narração
  conferir    - Compara transcrição vs roteiro
  mixar       - Gera mix a partir de plano JSON
  render      - Render uma cena específica
  recortar    - Processa imagens (rembg/elipse/cor)
  nova-cena   - Cria nova cena a partir do template

Utilitários:
  status      - Mostra estado do projeto (estado.py status)
  estado      - Wrapper para ferramentas/util/estado.py (passa args restantes)

Exemplos:
  rv.sh retrovisage-01 iniciar
  rv.sh retrovisage-01 alinhar Narracao/narracao_v01.wav
  rv.sh retrovisage-01 pausas 3 --frase 0.40 --paragrafo 0.90
  rv.sh retrovisage-01 mapa
  rv.sh retrovisage-01 imagens --so img01,img05
  rv.sh retrovisage-01 animar cena-intro
  rv.sh retrovisage-01 som plano_mix.json
  rv.sh retrovisage-01 final
  rv.sh retrovisage-01 status
  rv.sh retrovisage-01 estado --etapa mapa=concluido
USAGE
  exit 1
fi

PROJETO_DIR="$ROOT/projects/$PROJETO"
if [[ ! -d "$PROJETO_DIR" ]]; then
  echo "ERRO: Projeto '$PROJETO' não encontrado em $PROJETO_DIR"
  exit 1
fi

# Ambiente Python: primeiro o do repo (scripts/instalar-local.sh), depois o de ~/
VENV_PY="$ROOT/.venv-edicao/bin/python"
[[ -x "$VENV_PY" ]] || VENV_PY="$HOME/.venv-edicao/bin/python"
[[ -x "$VENV_PY" ]] || VENV_PY="python3"

# Função para rodar ferramentas de áudio
run_audio() {
  local script="$1"; shift
  "$VENV_PY" "$ROOT/ferramentas/audio/$script" "$PROJETO_DIR" "$@"
}

# Função para rodar ferramentas de vídeo
run_video() {
  local script="$1"; shift
  "$VENV_PY" "$ROOT/ferramentas/video/$script" "$PROJETO_DIR" "$@"
}

# Função para rodar skills (via Claude Code / OpenCode)
run_skill() {
  local skill="$1"
  echo ">>> Rodando skill: $skill"
  echo "    Projeto: $PROJETO"
  echo    ""
  echo "    [INTEGRAÇÃO PENDENTE: chamar skill via OpenCode/Claude Code]"
  echo "    Por enquanto, execute manualmente no terminal do OpenCode:"
  echo "    /$skill $PROJETO_DIR"
}

case "$ETAPA" in
  # --- FLUXO PRINCIPAL (skills) ---
  iniciar)
    run_skill video-iniciar
    ;;
  preparar)
    run_skill video-preparar
    ;;
  mapa)
    run_skill video-mapa
    ;;
  imagens)
    run_skill video-imagens
    ;;
  animar)
    run_skill video-animar
    ;;
  som)
    run_skill video-som
    ;;
  final)
    run_skill video-final
    ;;

  # --- FERRAMENTAS INDIVIDUAIS ---
  alinhar)
    # rv.sh projeto alinhar <audio.wav> [--idioma pt]
    run_audio alinhar.py "${ARGS[@]}"
    ;;
  pausas)
    # rv.sh projeto pausas <versao> [--frase 0.40] [--paragrafo 0.90] [--min 0.20] [--folga 0.15] [--alongar "42.2=0.5"]
    run_audio pausas.py "${ARGS[@]}"
    ;;
  conferir)
    # rv.sh projeto conferir [roteiro.md]
    run_audio conferir_roteiro.py "${ARGS[@]}"
    ;;
  conferir-partes)
    # rv.sh projeto conferir-partes <pasta-audios> <pasta-textos> [--idioma fr]
    run_audio conferir_partes.py "${ARGS[@]}"
    ;;
  mixar)
    # rv.sh projeto mixar <plano.json> <saida.wav>
    run_audio mixar.py "${ARGS[@]}"
    ;;
  final)
    # rv.sh projeto final <video.mp4> <mix.wav> <saida.mp4>
    run_audio final.py "${ARGS[@]}"
    ;;
  recortar)
    # rv.sh projeto recortar <spec.json> [--so img01,img02]
    run_video recortar.py "${ARGS[@]}"
    ;;
  nova-cena)
    # rv.sh projeto nova-cena <nome-cena>
    run_video nova-cena.py "${ARGS[@]}"
    ;;
  montar-html)
    # rv.sh projeto montar-html <pasta-hyperframes>
    run_video montar_html.py "${ARGS[@]}"
    ;;

  # --- UTILITÁRIOS ---
  status)
    "$VENV_PY" "$ROOT/ferramentas/util/estado.py" "$PROJETO_DIR" status
    ;;
  estado)
    # Passa args direto para estado.py
    "$VENV_PY" "$ROOT/ferramentas/util/estado.py" "$PROJETO_DIR" "${ARGS[@]}"
    ;;
  instalar)
    bash "$ROOT/ferramentas/util/instalar.sh"
    ;;

  *)
    echo "ERRO: Etapa desconhecida '$ETAPA'"
    echo "Use 'rv.sh $PROJETO' sem args para ver ajuda"
    exit 1
    ;;
esac