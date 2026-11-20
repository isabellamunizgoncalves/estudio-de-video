---
name: video-som
description: "Escolhe e encaixa a música de fundo e os poucos efeitos sonoros discretos do vídeo do Rétrovisage, com o volume certo sob a voz. Use em /video-som, após a video-animar."
---

# video-som

O som entra por último, sobre a narração e as animações já travadas. Decide a música de cada trecho e os poucos efeitos, com os níveis ajustados. Não renderiza o vídeo final (isso é da `video-final`).

- **Lê:** blocos `cenas`, `renders`, `eventos_som`; capítulos; perfil `estilo-som.md`; `biblioteca/musica/` e `biblioteca/sfx/` (índices); `.claude/skills/fluxo-de-edicao/guias/etapa-sfx.md`
- **Escreve:** blocos `musica` e `sfx` no estado; `_CLAUDE/som/` (o plano e os arquivos usados); `_CLAUDE/creditos.json`
- **Próximo passo:** `/video-final`

Se a `video-animar` não estiver `concluido`, pare e sugira terminá-la.

## Música (`mus01`, `mus02`…)
- **Clima** (perfil): França de antigamente, leve e curiosa: acordeão, piano, jazz e valsa dos anos 1920–50, cordas suaves. Pode mudar por capítulo, seguindo o tom da história (alegre, nostálgico, tenso).
- **Fontes** com licença clara (pesquise o estado atual): Pixabay Music, Free Music Archive, Incompetech (CC BY, pede crédito), YouTube Audio Library (Isabella baixa: não tem acesso daqui). Domínio bloqueado: mande a lista de sugestões (clima, termos de busca, links) e o nome de arquivo esperado para ela subir em `Musica/`.
- **Encaixe:** troca de faixa nas trocas de capítulo, com crossfade de ~2–3 s; nada de música começando ou parando no meio de frase.
- **Volume:** a voz sempre clara. Música baixa sob a voz (ducking), um pouco mais alta só nas telas de capítulo e nos respiros sem fala. Alvo inicial: música ~18–22 dB abaixo da voz (ajustar pelo feedback e anotar no perfil).
- **Biblioteca:** faixa aprovada vai para `biblioteca/musica/` do repositório do fluxo, com licença e crédito. Assim o canal ganha um som reconhecível.

## Efeitos (`sfx01`…), poucos e discretos
- Só em animações e viradas, seguindo os `eventos_som` (perfil: papel rasgando, fita colando, página virando, whoosh suave, clique de câmera antiga, máquina de escrever nas datas).
- Princípios do `etapa-sfx.md`, com o perfil por cima: o som segue o que se vê; um som por momento (aqui raramente mais de um); o pico do whoosh no frame em que o elemento freia; não repetir o mesmo arquivo em ~20 s; nível bem abaixo da voz.
- **Biblioteca** `biblioteca/sfx/<categoria>/` com índice gerado por script (duração útil, tempo até o pico). Na primeira vez, monte uma base pequena com sons gratuitos de licença clara (ou peça para ela subir), só nas categorias do perfil.
- Faltou som? Melhor sem do que um ruim. Anote numa lista de sons que faltam.

## Scripts (`ferramentas/`, escritos na primeira vez)
| Script | O que faz | Armadilhas |
|---|---|---|
| `indexar_sons.py` | índice da biblioteca: duração útil, tempo até o pico, loudness | pular o silêncio do começo |
| `mixar.py` | monta voz + música + efeitos com os níveis, ducking e fades, gera `mix_vNN.wav` | loudness da voz em LUFS como base; fades de ~10 ms em todo efeito; teto de pico; nada mais alto que a voz |

## Passo a passo
1. Status. Plano da música por capítulo e dos efeitos → mostrar numa lista curta por número, antes de buscar.
2. Buscar (ou mandar a lista de sugestões) → folha de opções por faixa quando houver mais de uma boa.
3. Mix → rascunho 720p com o vídeo do trecho → mandar pela conversa.

## Resumo no chat
As faixas (com crédito), quantos efeitos, o que faltou. Marque `aguardando_aprovacao`.

## Revisão
- "mus02 mais baixa": 3 dB a menos; "troca a mus03": outra do mesmo clima; "sfx05 tira"; "sfx03 um quadro antes".
- Anotar aprendizados (níveis e climas preferidos vão para o perfil).

## Aprovação
`concluido`, faixas e sons aprovados para a biblioteca, `/clear` e `/video`.

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca usar música ou som sem licença e crédito anotados.
- Nunca mover, renomear ou apagar arquivos do projeto.