# Motor: Edge TTS

Vozes neurais da Microsoft pelo pacote [`edge-tts`](https://github.com/rany2/edge-tts).
Rápido e sem GPU: cerca de **4 minutos para 28 minutos de áudio**.

Voz padrão **Remy** (`fr-FR-RemyMultilingualNeural`), escolhida por Isabella em 19/11/2026 depois
de comparar com Voice Studio, Kokoro, Orpheus, Supertonic e Pocket TTS.

## Privacidade

O áudio é gerado **nos servidores da Microsoft**: o texto do roteiro sai da máquina.
Aceito para o canal; avisar de novo só se o texto tiver algo pessoal.

## Ambiente

```bash
.venv-edicao/bin/python -c "import edge_tts"
```

Faltando: `.venv-edicao/bin/pip install edge-tts`. Precisa de `ffmpeg` e de internet.

## Comando

Da raiz do repo, em segundo plano:

```bash
.venv-edicao/bin/python skills/video-narrar/scripts/narrar_edge.py --projeto projects/<slug>
```

| Opção | Padrão | Para quê |
|---|---|---|
| `--voz` | `fr-FR-RemyMultilingualNeural` | outra voz (`fr-FR-HenriNeural`, `fr-FR-DeniseNeural`…) |
| `--rate` | `-8%` | velocidade (mais negativo = mais calmo) |
| `--pausa` | `0.75` | silêncio entre parágrafos, em segundos |
| `--pausa-curta` | `1.1` | silêncio depois de frase de impacto isolada (até 6 palavras) |
| `--saida` | `Narracao/narracao_vNN.wav` | outro arquivo (testes) |

Lista completa de vozes: `.venv-edicao/bin/edge-tts --list-voices`

## Problemas comuns

| Erro | Causa | O que fazer |
|---|---|---|
| `NoAudioReceived` | nome de voz errado | conferir com `edge-tts --list-voices` (é `Remy`, não `Remi`) |
| erro de conexão / 403 | sem internet ou serviço instável | tentar de novo; o script já repete cada parágrafo até 4 vezes |
| `ffmpeg: not found` | ffmpeg ausente | `sudo apt install ffmpeg` (num terminal fora do app do Claude) |
