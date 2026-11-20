# Fluxo — do tema ao vídeo final

Cada vídeo vive em `projects/<slug>/`. Cada etapa lê o que a anterior gravou e grava onde a próxima lê. Para trocar a ferramenta de uma etapa (outra voz, outro roteirista), basta manter o mesmo arquivo de saída.

## Sequência

| # | Etapa | Skill | Lê | Grava |
|---|---|---|---|---|
| 1 | Roteiro | `video-roteiro` | tema, link, comentários, `perfis/<canal>/roteiro.md` | `Roteiro/roteiro.md` + `Roteiro/roteiro.txt` |
| 2 | Humanizar | `video-humanizar` | `Roteiro/roteiro.txt` | `Roteiro/roteiro_humanizado.txt` |
| 3 | Abrir o vídeo | `/video-iniciar` | `Roteiro/` | `_CLAUDE/projeto.json`, `_CLAUDE/briefing.md`, `_CLAUDE/roteiro-capitulos.md` |
| 4 | Narração | `video-narrar` (motor plugável) | `Roteiro/roteiro_humanizado.txt` (senão `roteiro.txt`) | `Narracao/narracao_vNN.wav` (+ ficha `.json`) |
| 5 | Preparar | `/video-preparar` | `Narracao/`, `Roteiro/`, capítulos | `_CLAUDE/transcricao/`, `_CLAUDE/narracao/narracao_vNN.wav` (pausas ajustadas) |
| 6 | Mapa | `/video-mapa` | transcrição, briefing, perfil | `_CLAUDE/mapa/mapa_vNN.md`, bloco `cenas` |
| 7 | Imagens | `/video-imagens` | mapa | `_CLAUDE/imagens/`, `_CLAUDE/creditos.json` |
| 8 | Animar | `/video-animar` | mapa, imagens, transcrição | `_CLAUDE/animacoes/`, `_CLAUDE/renders/` |
| 9 | Som | `/video-som` | renders, narração ajustada | `_CLAUDE/som/mix_vNN.wav` |
| 10 | Final | `/video-final` | animações, mix | `_CLAUDE/renders/final/<slug>_final_vNN.mp4`, `_CLAUDE/entrega/` |

O `/video` mostra em que etapa o vídeo está e abre a próxima, em qualquer ponto da cadeia.

## Regras do contrato

- **Quem é dono de quê:** `Roteiro/` é das skills de roteiro, `Narracao/` é da narração (ou de Isabella), `_CLAUDE/` é das skills de edição. Uma etapa nunca sobrescreve o que é de outra.
- **Versões só sobem:** `narracao_v01`, `v02`… Gerar de novo cria uma versão nova; a anterior fica.
- **Estado só pela edição:** apenas as skills `rv-*` escrevem em `_CLAUDE/projeto.json`, sempre via `ferramentas/util/estado.py`.
- **Narração trava o resto:** se a narração mudar depois do mapa, o mapa e as animações precisam ser refeitos.

## Começar um vídeo

```bash
./scripts/novo-projeto.sh --proximo       # mostra o próximo retrovisage-NN livre
./scripts/novo-projeto.sh retrovisage-04  # cria Roteiro/ Narracao/ Imagens/ Musica/ _CLAUDE/
```

As skills de roteiro e a `/video-iniciar` rodam esse script sozinhas quando a pasta ainda não existe.
