---
name: video-animar
description: "Monta e anima as colagens do vídeo do Rétrovisage cena a cena (fundos, recortes, fitas, textos, parallax e o movimento nas fotos) com o HyperFrames e renderiza por trecho para Isabella assistir. Use em /video-animar, após a video-imagens, ou para um trecho ('anima o gancho')."
---

# video-animar

Constrói cada cena aprovada no mapa e renderiza. É a etapa mais longa e a que mais depende do ofício. Inclui o "movimento de câmera": sem apresentador, a câmera é o movimento dentro da própria colagem.

- **Lê:** blocos `cenas` e `imagens`; `_CLAUDE/transcricao/` (tempos por palavra, sob demanda); perfil: `identidade.md`, `estilo-motion.md`, `estilo-camera.md`, `catalogo.md`, peças-base (se houver); `.claude/skills/fluxo-de-edicao/guias/oficio-motion.md` e `hyperframes.md`
- **Escreve:** `_CLAUDE/animacoes/<trecho>/` (projetos HyperFrames, a fonte das animações); `_CLAUDE/renders/` (vídeos, refeitos a partir dos projetos); bloco `renders` e `eventos_som` no estado
- **Próximo passo:** `/video-som`

Se a `video-imagens` não estiver `concluido`, pare e sugira terminá-la (cena com imagem faltando pode ir com marcador visível, se ela quiser seguir).

## Ofício (do `oficio-motion.md`, com o perfil por cima)
- **Uma coisa protagonista por vez.** A cena se constrói: um elemento entra, assenta, o próximo entra.
- **Entradas:** imagens deslizam ~1,0–1,2 s (`power3.out`); fitas e rótulos caem em ~0,25–0,3 s (`back.out(1.6)`) e assentam inclinados. Saídas mais curtas (`power2.in`).
- **Movimento contínuo:** aproximação e deriva em **dois contêineres aninhados** (o de fora aproxima, o de dentro deriva linear): nunca encadear um ease-out que para com um linear depois (o zoom "engasga"). Alternar a direção entre cenas.
- **Parallax:** camadas com velocidades diferentes (fundo mais lento, frente mais rápida), sutil.
- **Trocas de cena:** variar (rasgo de papel, troca de fundo com recorte novo, deslize com speed ramp); não repetir a mesma em sequência.
- **Diagramação:** cada elemento alinhado ao que acompanha; texto dentro da área segura (80% do quadro), no mínimo 28 px em 1080p.
- **Sincronia:** o elemento de uma palavra entra **na palavra**. O tempo 0 da composição é o início do trecho; cada gatilho em `tempo_da_palavra − início`.

- **Vídeos (`vidNNN`) dentro da colagem:** `<video muted>` num quadro de foto (borda branca, sombra) ou recortado com borda rasgada; mesmo tratamento de cor da foto (P&B só se for ambiente antigo). Entram e saem como as fotos; o movimento próprio do vídeo substitui a aproximação lenta (no máximo +3%). Conferir no snapshot que o quadro do vídeo bate com o tempo (o HyperFrames extrai os quadros do arquivo).
- **Contraste de traços finos:** círculos à mão, fios, setas e contornos na cor do fundo somem (café sobre café). Conferir em snapshot; sobre café, usar creme. (natal-1962)

## HyperFrames
Siga `hyperframes.md` (versão fixa por vídeo, anotada no estado; CSS embutido; `fromTo` com `lazy: false`; `immediateRender: false` quando começa visível; origem da transformação fixada; layout medido dentro de `document.fonts.ready`; desfoque de movimento `filter`). Fontes do perfil (Anton, Playfair Display, Special Elite) baixadas do Google Fonts e embutidas.
- **Composição:** um projeto por **trecho** (gancho, capítulo ou faixa de minutos), com as cenas encadeadas numa timeline só. Assim as trocas de cena ficam contínuas.
- **Saída:** MP4 1920x1080, 30 qps, sem áudio. A voz e a música entram na `video-final`.
- **Rascunho de revisão** em 720p, com a narração por baixo (mix rápido por FFmpeg), para ela assistir com a voz.
- **Eventos para o som:** ao construir, anote tudo o que chega, cai, rasga, cola, vira, revela (tempo, tipo em palavras livres, força, descrição). A `video-som` parte disso.

## Passo a passo
1. Status: quais trechos já foram feitos. Pergunte o trecho, se ela não disse (sugestão: o **gancho primeiro**, sozinho, para acertar o estilo).
2. **Primeira vez de todas:** antes do gancho, uma **cena de teste** curta (~8 s) com o estilo do perfil, renderizada e mandada para ela. Só com o "sim" dela o estilo vale para o vídeo. Anote o que foi confirmado em `perfis/retrovisage/validacao.md`.
3. Por cena: construir → `check` → snapshots nos momentos-chave e **olhar** → ajustar.
4. Render em segundo plano. Conferir o arquivo: resolução, taxa, número de quadros igual à duração do trecho, um ou dois quadros.
5. Rascunho 720p com a voz → mandar pela conversa.
6. Salve os projetos de animação e o estado (renders podem ser refeitos a partir deles).

## Resumo no chat
O trecho, as cenas feitas, o que não deu para fazer como no mapa (e por quê), imagens com marcador. Marque o trecho `aguardando_aprovacao`.

## Revisão
- Por número ou minuto: "cn014 mais devagar", "no 3:40 troca a direção do zoom". Ajustar só o citado, versão nova, juntar pedidos antes de renderizar.
- **Feedback geral** ("sem vida", "amador", "parado"): **refazer** a cena, não retocar. Releia as referências (`perfis/retrovisage/analises/sintese.md`), diga numa frase a nova direção e construa de novo.
- Anotar aprendizados no caderno.

## Aprovação
Trecho aprovado → `concluido` no trecho; todos aprovados → etapa `concluido`. Olhe o que deu certo: padrão repetido vira item do `catalogo.md`; elemento que ficou bom (fita, moldura rasgada, fundo) vira **peça-base** no perfil (CSS + função JS), com o "sim" dela. `/clear` e `/video`.

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Nunca sobrescrever um render entregue: `_v01`, `_v02`…
- Nada da marca Vox.