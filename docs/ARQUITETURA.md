# Arquitetura — estúdio de vídeo

## Princípios

1. **Fonte única**: cada skill existe em um só lugar (`skills/<skill>/`). Tudo o mais
   (`.claude/skills/`, `~/.claude/skills/`) é symlink.
2. **Método ≠ estilo**: a skill traz o método, igual para qualquer canal; o estilo do canal vem de
   `perfis/<canal>/`. Uma skill que só serve a um canal está no lugar errado.
3. **Código ≠ dados**: skills, ferramentas, perfis e biblioteca são versionados; vídeos
   (`projects/`) não.
4. **Etapas independentes**: as etapas trocam só arquivos (`roteiro.md` → `narracao.wav` →
   `final.mp4`). Dá para trocar a ferramenta de uma etapa sem tocar nas outras.
5. **Repos públicos isolados**: skills vindas de repositórios públicos entram como submódulo e são
   atualizadas com `git submodule update --remote`, nunca editadas aqui.

## Estrutura

Veja o mapa no [README](../README.md#estrutura). Resumo das responsabilidades:

| Pasta | Papel | Versionado |
|---|---|---|
| `skills/video/` | mestra: estado do vídeo e abertura da etapa certa | sim |
| `skills/video-*/` | as 10 etapas da cadeia, do roteiro ao MP4 | sim |
| `skills/fluxo-de-edicao/` | meta-skill: monta o fluxo de um canal novo | submódulo externo |
| `.claude/skills/` | links relativos para as skills, para carregarem ao abrir o repo | sim |
| `ferramentas/` | scripts Python chamados pelas skills (`audio/`, `video/`, `util/`, `_lib/`) | sim |
| `perfis/<canal>/` | estilo do canal: roteiro, identidade, motion, câmera, cortes, som | sim |
| `biblioteca/` | músicas, SFX, texturas compartilhadas | só índices e créditos |
| `templates/` | template de cena Hyperframes, formato global | sim |
| `projects/` | um vídeo por pasta | só `_templates/` |
| `scripts/` | atalhos (`novo-projeto`, `video`, `skill-install`, `sync-perfil`) | sim |

## Fluxo de dados

```
[video-roteiro]    ──► Roteiro/roteiro.md + roteiro.txt
[video-humanizar]  ──► Roteiro/roteiro_humanizado.txt
[video-iniciar]    ──► _CLAUDE/projeto.json, briefing, capítulos
[video-narrar]     ──► Narracao/narracao_vNN.wav (+ ficha .json)
[video-preparar]   ──► _CLAUDE/transcricao/ + _CLAUDE/narracao/narracao_vNN.wav (pausas ajustadas)
[video-mapa]       ──► _CLAUDE/mapa/mapa_vNN.md
[video-imagens]    ──► _CLAUDE/imagens/ + _CLAUDE/creditos.json
[video-animar]     ──► _CLAUDE/animacoes/ + _CLAUDE/renders/
[video-som]        ──► _CLAUDE/som/mix_vNN.wav
[video-final]      ──► _CLAUDE/renders/final/<slug>_final_vNN.mp4 (loudnorm -14 LUFS)
```

Tabela completa (o que cada etapa lê e grava) em [FLUXO.md](FLUXO.md).

## Convenções

| Tipo | Padrão | Exemplo |
|---|---|---|
| Projeto | `canal-NN` | `retrovisage-04` |
| Skill da cadeia | `video-{etapa}` | `video-mapa` |
| Cena | `cena-{slug}` | `cena-escola-1962` |
| Narração / mix / final | `{tipo}_v{NN}` | `narracao_v02.wav`, `final_v01.mp4` |
| Motor de voz | `motores/{motor}.md` | `motores/edge.md` |

## Regras de ouro

1. Durante a produção de um vídeo, não edite `skills/`, `ferramentas/`, `perfis/`, `biblioteca/`,
   `templates/`.
2. Tudo que muda por vídeo fica em `projects/<projeto>/`.
3. `_CLAUDE/` é estado interno: nunca versionar.
4. Versões só sobem (`v01`, `v02`…), nunca sobrescreva.
5. Mudou o estilo? Mexa em `perfis/<canal>/` e aponte o projeto para ele
   (`scripts/sync-perfil.sh`).

## Como escalar

- **Nova etapa** (thumbnail, publicação, shorts): `skills/video-<etapa>/SKILL.md` +
  `./scripts/skill-install.sh --repo`. Acrescente a linha em `FLUXO.md` dizendo o que ela lê e grava.
- **Novo canal**: rode `/fluxo-de-edicao`. Ela entrevista e escreve o perfil e as skills daquele
  canal, em vez de copiar pastas à mão.
- **Trocar o motor de voz**: novo `skills/video-narrar/motores/<motor>.md` + script com a mesma
  interface do `narrar_edge.py`, entregando o mesmo `Narracao/narracao_vNN.wav`. Nada mais muda.
