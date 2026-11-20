# Estúdio de vídeo

Produção de vídeo do começo ao fim com o Claude Code: **roteiro → narração → edição**.

Serve **qualquer canal**. O que muda de um canal para outro — idioma, público, estilo de escrita,
identidade visual, som — vive em `perfis/`. As skills são as mesmas para todos.

```
/video-roteiro → /video-humanizar → /video-iniciar → /video-narrar → /video-preparar
→ /video-mapa → /video-imagens → /video-animar → /video-som → /video-final
```

`/video` é o ponto de entrada: diz em que etapa cada vídeo está e abre a próxima.

## As 11 skills

| # | Skill | O que faz |
|---|---|---|
| — | **`/video`** | mestra: onde o vídeo está, o que falta, abre a etapa certa |
| 1 | `/video-roteiro` | escreve o roteiro a partir do tema + comentários do público, no estilo do perfil |
| 2 | `/video-humanizar` | pontuação e pausas para a voz de IA ler como gente |
| 3 | `/video-iniciar` | abre o vídeo: pastas, briefing, divisão em capítulos |
| 4 | `/video-narrar` | gera a narração (motor plugável; padrão Edge TTS, voz Remy) |
| 5 | `/video-preparar` | alinha a voz ao texto, confere e ajusta as pausas |
| 6 | `/video-mapa` | planeja cena a cena: que imagem, que colagem, que movimento |
| 7 | `/video-imagens` | busca fotos e vídeos com fonte e licença, e prepara os recortes |
| 8 | `/video-animar` | monta e anima as colagens, renderiza por trecho |
| 9 | `/video-som` | música de fundo e efeitos, no volume certo sob a voz |
| 10 | `/video-final` | junta tudo e gera o MP4 em 1080p + os créditos |

Mais uma, fora da cadeia: **`/fluxo-de-edicao`** — a meta-skill que entrevista você e **escreve as
skills de um canal novo**. É por ela que se começa um segundo canal, não copiando pastas.

## Estrutura

```
estudio-de-video/
├── skills/                  # FONTE ÚNICA das skills (pasta plana)
│   ├── video/               # mestra
│   ├── video-roteiro/ -humanizar/ -narrar/
│   ├── video-iniciar/ -preparar/ -mapa/ -imagens/ -animar/ -som/ -final/
│   └── fluxo-de-edicao/     # submódulo → LeiteZ/fluxo-de-edicao (canal novo)
│
├── .claude/skills/          # links relativos → skills/ (carregam ao abrir o repo)
│
├── perfis/                  # O ESTILO DE CADA CANAL
│   └── retrovisage/         # roteiro.md, identidade.md, estilo-*.md, peças, fontes
│
├── ferramentas/             # scripts Python usados pelas skills (audio/ video/ util/ _lib/)
├── biblioteca/              # músicas, SFX e texturas compartilhadas
├── templates/               # template de cena Hyperframes + formato global
│
├── projects/                # um vídeo por pasta (fora do git, só _templates/ versionado)
│   └── <canal>-NN/  Roteiro/ Narracao/ Imagens/ Musica/ _CLAUDE/
│
├── scripts/                 # atalhos de linha de comando
└── docs/                    # arquitetura, fluxo, montagem, roteiros de exemplo
```

## Uso rápido

```bash
./scripts/skill-install.sh --list
```

```bash
./scripts/skill-install.sh --repo
```

```bash
./scripts/skill-install.sh
```

```bash
bash scripts/instalar-local.sh
```

```bash
./scripts/novo-projeto.sh --proximo retrovisage
```

```bash
./scripts/video.sh retrovisage-04 status
```

O primeiro lista as skills; `--repo` liga em `.claude/skills/` deste repositório e sem argumento
liga em `~/.claude/skills` (uso global). O `instalar-local.sh` monta o ambiente Python das
ferramentas. Os dois últimos criam um vídeo novo e mostram em que etapa ele está.

Clonando pela primeira vez, traga também o submódulo:

```bash
git clone --recurse-submodules https://github.com/isabellamunizgoncalves/estudio-de-video
```

## Como crescer sem bagunçar

- **Nova skill** → `skills/<nome>/SKILL.md`, depois `./scripts/skill-install.sh --repo`.
- **Novo canal** → `/fluxo-de-edicao` monta o perfil e as skills dele. Nada de copiar pastas.
- **Novo estilo no mesmo canal** → mexa em `perfis/<canal>/`, não nas skills.
- **Outro motor de voz** → `skills/video-narrar/motores/<motor>.md` + script com a mesma interface.
  O resto da cadeia não muda.
- **Novo vídeo** → `scripts/novo-projeto.sh`. Nada de vídeo vai para o git.

Detalhes em [docs/ARQUITETURA.md](docs/ARQUITETURA.md) e [docs/FLUXO.md](docs/FLUXO.md).

## Créditos

- Narração: [rany2/edge-tts](https://github.com/rany2/edge-tts) — vozes neurais da Microsoft, sem GPU.
- Fluxo de edição: as skills `video-iniciar … video-final` nasceram da meta-skill
  [LeiteZ/fluxo-de-edicao](https://github.com/LeiteZ/fluxo-de-edicao).
