---
name: video-iniciar
description: "Abre um vídeo novo do Rétrovisage: cria a pasta do vídeo em projects/, recebe o roteiro, organiza o briefing e divide o roteiro em gancho e capítulos. Use em /video-iniciar, para começar um vídeo novo."
---

# video-iniciar

Abre o projeto e organiza o briefing. Não analisa áudio nem imagem.

- **Lê:** `Roteiro/` (o que as skills de roteiro gravaram, ou o que Isabella subiu), o perfil `perfis/retrovisage/identidade.md` (só para o formato)
- **Escreve:** `_CLAUDE/projeto.json`, `_CLAUDE/briefing.md`, `_CLAUDE/roteiro-capitulos.md`, `_CLAUDE/aprendizados.md` (vazio)
- **Próximo passo:** a narração (`/video-narrar`), depois `/video-preparar`

## Passo a passo
1. **Regras comuns** (seção 0): ambiente e onde fica cada vídeo.
2. **A pasta do vídeo.** Se o roteiro já foi escrito por aqui, a pasta `projects/<slug>/` já existe: use-a. Senão, combine com Isabella um nome curto, sem acento e sem espaço (padrão `retrovisage-NN`, o próximo número livre em `projects/`) e rode `scripts/novo-projeto.sh <slug>`. Ele cria `Roteiro/`, `Narracao/`, `Imagens/`, `Musica/` e `_CLAUDE/`.
   - **Projeto já iniciado** (`_CLAUDE/projeto.json` existe): não sobrescreva nada; mostre o status e pergunte se é só para atualizar o briefing.
3. **Estado inicial:** `ferramentas/util/estado.py projects/<slug> --criar <slug>` (cria o `projeto.json` com perfil, formato 1920x1080 30 qps e todas as etapas `pendente`, esta `em_andamento`).
4. **Roteiro:** use o que estiver em `Roteiro/` (`roteiro.md`, `roteiro.txt`, `roteiro_humanizado.txt`). Vazio: peça para ela colar no chat (salve como `Roteiro/roteiro.md`) ou subir o arquivo (texto, .docx ou .pdf). Nunca mude o texto dela.
5. **Briefing:** numa mensagem curta, sem formulário: "Me conta, do jeito que vier, sobre o que é esse vídeo e qualquer ideia que você já tenha (imagens, clima, música)." Organize sem inventar: preserve as palavras e a intenção dela. Seções: sobre o vídeo, direcionamentos gerais, observações por etapa (imagens, animações, som). Omita as vazias. Salve e mostre.
6. **Capítulos:** proponha a divisão do roteiro em **gancho** (até a promessa do vídeo) + capítulos (`c01`, `c02`…), com o título de cada um e a frase em que começa. Use os títulos que ela já escreveu; se não houver, proponha. Mostre numa lista curta e espere o "ok".
7. **Encerrar:** marque `concluido` e diga o que falta para a próxima etapa: a narração em `Narracao/`. Ofereça a `/video-narrar` (lê `Roteiro/roteiro_humanizado.txt`, ou `roteiro.txt`); se ela preferir outra ferramenta, basta colocar o `.wav` em `Narracao/`.

## Resumo no chat
A pasta do vídeo (`projects/<slug>/`), os capítulos e o próximo passo (narração).

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Não acrescentar tom, público ou ideia que ela não disse.