# Template de vídeo

`scripts/novo-projeto.sh <slug>` copia `pastas/` para `projects/<slug>/`:

```
projects/<slug>/
├── Roteiro/    roteiro.md, roteiro.txt, roteiro_humanizado.txt   (skills de roteiro)
├── Narracao/   narracao_vNN.wav (+ .json)                       (video-narrar ou Isabella)
├── Imagens/    o que Isabella sobe à mão
├── Musica/     o que Isabella sobe à mão
└── _CLAUDE/    estado e tudo que as skills de edição geram
```

O `_CLAUDE/projeto.json` não vem do template: a `/video-iniciar` cria com `ferramentas/util/estado.py projects/<slug> --criar <slug>`.

Contrato completo de arquivos entre as etapas: `docs/FLUXO.md`.
