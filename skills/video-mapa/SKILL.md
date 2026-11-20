---
name: video-mapa
description: "Planeja o vídeo inteiro do Rétrovisage, cena a cena: que imagem aparece em cada trecho da narração, que colagem, que animação, que texto na tela e que movimento. Não anima nada: Isabella aprova o plano pelo chat. Use em /video-mapa, após a video-preparar."
---

# video-mapa

A etapa que mais decide a qualidade do vídeo. Planeja cada cena: o que aparece, como se monta a colagem, que poucos textos entram e como tudo se move. **Não anima nada**: propõe no chat, ajusta com Isabella e grava o plano. Mudar aqui é barato; depois do render, um conceito fraco custa uma rodada inteira.

- **Lê:** `_CLAUDE/transcricao/frases.md`, `_CLAUDE/briefing.md`, capítulos; perfil: `identidade.md`, `estilo-motion.md`, `estilo-camera.md`, `catalogo.md`; `.claude/skills/fluxo-de-edicao/guias/oficio-motion.md`
- **Escreve:** bloco `cenas` no estado; `_CLAUDE/mapa/mapa_vNN.md` (o plano legível)
- **Próximo passo:** `/video-imagens`

Se a `video-preparar` não estiver `concluido`, pare e sugira terminá-la.

## Princípio
- **O conteúdo decide a cena.** Para cada trecho da história, a imagem e a colagem que contam melhor *aquele* momento. Nada de encaixar a fala num template.
- **O estilo é constante:** colagem editorial colorida (fotos de arquivo P&B recortadas sobre fundos vivos texturizados), definida no perfil.
- **O catálogo é repertório, nunca obrigação.** No gancho, um conceito próprio do assunto vale mais.
- **Nada fica parado:** toda cena tem movimento (perfil `estilo-camera.md`).

## 1. Trechos e ritmo
- Gancho, capítulos e fechamento vêm da `video-preparar`. Confirme numa linha ("Gancho até 00:52, 5 capítulos, fechamento a partir de 14:10. Confere?").
- **Ritmo** (perfil §4): gancho troca a cada ~2–4 s; corpo, cena nova a cada **8–15 s**; dentro da cena, um elemento novo a cada ~1,5–3 s. Acima de ~15 s, dividir.
- Planeje **o gancho primeiro e com mais detalhe**, quase frase a frase. Num vídeo longo, aprove por trecho: gancho → capítulos.

## 2. Cada cena (`cn001`, `cn002`…)
| Campo | O que descreve |
|---|---|
| tempo | início e fim (da narração ajustada), frase de início |
| conceito | a ideia visual numa frase, amarrada ao que está sendo contado |
| fundo | cor do perfil + textura (céu, papel, jornal, padrão) |
| imagens | o que mostrar (ex.: "padaria parisiense anos 1930, fachada"), com id `img001`… |
| construção | a ordem em que os elementos entram, cada um com a **palavra-gatilho** |
| texto | só quando merece: data, lugar, nome, número, palavra-chave (sem legenda) |
| movimento | aproximação, deslize ou parallax (camadas), direção |
| troca | como passa para a próxima (rasgo de papel, troca de fundo, deslize) |

**Storyboard detalhado** (camadas, batidas, herói, saída): obrigatório no gancho, opcional no corpo.

**Antes de mostrar, releia com estas perguntas:**
- A imagem nasce desta fala, ou serviria para qualquer vídeo?
- Estou repetindo a mesma fórmula (mesmo fundo, mesma entrada, mesma direção de movimento)?
- Há texto demais? (Perfil: no máximo ~1 destaque a cada 20–30 s no corpo.)

## 3. Telas especiais
- **Abertura e telas de capítulo:** título em Anton sobre fita, fundo de cor cheia texturizado (perfil).
- **Mapas e linhas do tempo:** quando a história cita lugares ou uma sequência de datas, um mapa da França ou uma linha do tempo desenhados no código explicam melhor que uma foto.
- **Vídeo de arquivo:** quando existir e servir, entra como imagem na colagem (recortado ou num quadro).

## 4. Imagens e vídeos
- **Vídeo curto (b-roll, `vidNNN`)** quando o movimento conta melhor que a foto: mãos escrevendo com pena, leite sendo servido, um Solex passando, neve caindo. Típico 3–8 s por uso; entra **dentro da colagem** (num quadro de foto, recortado ou com borda rasgada), nunca em tela cheia crua. Num vídeo longo, ~1 vídeo a cada 3–5 cenas; o resto, fotos animadas.
- Cada imagem com: descrição, época, lugar, tipo (foto de arquivo, cartão-postal, jornal de época, cartaz, mapa antigo, vídeo de arquivo) e **termos de busca em francês e em inglês** (os acervos franceses buscam melhor em francês: "boulangerie Paris 1930").
- Desenho, forma, mapa simples, fita, seta, moldura **não são imagem**: o render desenha no código.
- Liste `Imagens/` antes: ela pode já ter subido o que precisa.
- Cada vídeo com: descrição, duração desejada, se precisa ser de época (arquivo) ou pode ser atual "com cara de antigo", e termos de busca em inglês (os bancos buscam melhor em inglês).
- Esta etapa não busca nada; quem busca é a `video-imagens`.

## 5. Sincronia
- O elemento que representa uma palavra entra **na palavra** (tempo da transcrição).
- Texto na tela segura ~1–1,5 s depois da última palavra, salvo se a cena trocar antes.

## Revisão
Mostre o plano numerado, uma linha por cena: `cn014 · 3:12–3:24 · fundo azul · foto do mercado de Les Halles + data "1934" em fita · aproximação lenta`. Ela aprova, ajusta ou risca por número. Ao gravar de novo, preserve o status do que já foi aprovado. Anote aprendizados no caderno.

## Aprovação
Grave `mapa_vNN.md` e o bloco `cenas`, marque `concluido`. Se a narração mudar depois, o mapa precisa ser recalculado. Sugira `/clear` e `/video`.

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Não usar nada da marca Vox (logotipo, fontes, peças): só o estilo de colagem.