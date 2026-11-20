# CLAUDE.md

Responda sempre em português do Brasil.

Estúdio de produção de vídeo com o Claude Code: **roteiro → narração → edição**, do tema ao arquivo
final. Serve qualquer canal — o estilo de cada um vive em `perfis/`, não nas skills.
Visão geral em `README.md`; o contrato de arquivos entre as etapas em `docs/FLUXO.md`.

## Regras de organização

- Skills ficam só em `skills/<skill>/SKILL.md`, pasta plana, todas com o prefixo `video-`
  (a mestra é `video`). Não crie cópias em outros lugares; `.claude/skills/` e `~/.claude/skills`
  recebem apenas symlinks, via `scripts/skill-install.sh`.
- **O estilo é do perfil, não da skill.** Idioma, público, estrutura, tom, CTA, identidade visual e
  som vão para `perfis/<canal>/`. Uma skill que só serve a um canal está no lugar errado.
- Cada vídeo vive em `projects/<canal>-NN/` (`Roteiro/`, `Narracao/`, `Imagens/`, `Musica/`,
  `_CLAUDE/`). Ao mudar uma skill, mantenha o contrato de `docs/FLUXO.md`. Nunca grave saída de
  vídeo em `skills/`, `ferramentas/`, `perfis/`, `biblioteca/` ou `templates/`.
- `skills/fluxo-de-edicao/` é submódulo git (LeiteZ/fluxo-de-edicao): não edite; atualize com
  `git submodule update --remote`. É a meta-skill que **monta o fluxo de um canal novo** — ela não
  edita vídeo nenhum.
- Narração: skill `video-narrar`, com motor plugável em `skills/video-narrar/motores/`. Padrão hoje
  é **Edge TTS**, voz `fr-FR-RemyMultilingualNeural` (Remy), sobre o roteiro humanizado. Google AI
  Studio tem o encaixe pronto, a configurar. Voice Studio, Voicebox, Kokoro, Orpheus, Supertonic e
  Pocket TTS foram testados e descartados (lentos na CPU ou voz pior).
- Versões só sobem (`v01`, `v02`…). Nunca sobrescreva uma narração, um mix ou um render.
