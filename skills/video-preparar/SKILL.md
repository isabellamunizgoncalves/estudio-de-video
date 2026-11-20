---
name: video-preparar
description: "Prepara a narração do vídeo do Rétrovisage: confere o áudio, acha o tempo de cada palavra do roteiro (alinhamento), confere se a voz bate com o roteiro e ajusta as pausas longas demais. Use em /video-preparar, após a narração (video-narrar ou .wav subido) estar em Narracao/."
---

# video-preparar

Transforma a narração em algo que o Claude consegue ler: o tempo de cada palavra, a conferência com o roteiro e as pausas ajustadas. Também faz o papel da etapa de cortes: a voz é de IA (Edge TTS, voz Remy, ou outra ferramenta), sem hesitação nem take repetido, então cortar é só ajustar o ritmo.

- **Lê:** `Narracao/` (a versão mais recente, `narracao_vNN.wav`, e a ficha `.json` se houver), `Roteiro/` (o texto que foi narrado: `roteiro_humanizado.txt`, senão `roteiro.txt`/`roteiro.md`), `_CLAUDE/roteiro-capitulos.md`, `perfis/retrovisage/estilo-cortes.md`
- **Escreve:** bloco `narracao` e `transcricao` no estado; `_CLAUDE/transcricao/` (por palavra, para scripts; por frase, para o Claude); `_CLAUDE/narracao/narracao_v01.wav` (com as pausas ajustadas)
- **Próximo passo:** `/video-mapa`

Se a `video-iniciar` não estiver `concluido`, pare e sugira terminá-la.

## Ofício
- **O texto já existe:** o roteiro é a referência. A transcrição serve para achar **quando** cada palavra é dita e para conferir se a voz falou o que estava escrito.
- **Divergência voz × roteiro** (palavra trocada, trecho pulado, nome francês pronunciado errado, número lido errado): marque e mostre a Isabella com o minuto. Quem decide é ela; a correção é gerar de novo com a `/video-narrar` (sai `Narracao/narracao_vNN.wav` numa versão nova). Nunca "consertar" trocando o áudio.
- **Pausas:** a IA às vezes deixa pausas longas ou irregulares. Encurte as que passam do perfil (`estilo-cortes.md`); nunca corte no meio de palavra; sem pausa de menos de ~0,2 s entre frases (fica atropelado).
- **Capítulos:** marque o tempo de início de cada capítulo e do fim do gancho.
- Na dúvida, não corta e marca.

## Scripts (na pasta `ferramentas/`)
Na primeira vez, escreva o que faltar, teste e anote aqui o uso. Nos próximos vídeos, reaproveite.

| Script | O que faz | Armadilhas |
|---|---|---|
| `scripts/instalar-local.sh` | cria `.venv-edicao/` na raiz com WhisperX (CPU), PyTorch CPU, NumPy, OpenCV, PySceneDetect, rembg | sem GPU aqui: instale o PyTorch **CPU** (o pacote padrão puxa CUDA e gigabytes à toa); se `download.pytorch.org` estiver bloqueado, avise o domínio; rode em segundo plano |
| `inventario.py` | ffprobe da narração: duração, taxa, canais, picos | arquivo com silêncio longo no começo ou no fim: avisar |
| `alinhar.py` | WAV 16 kHz mono → WhisperX com alinhamento por palavra (idioma pt), roteiro e nomes próprios como contexto | o contexto pode fazer o modelo inventar frases: procure trechos com som e sem palavra e retranscreva **sem** contexto; nomes franceses mal reconhecidos: use a grafia do roteiro, mantendo o tempo |
| `conferir_roteiro.py` | compara palavra a palavra transcrição × roteiro (alinhamento de sequências) e lista divergências com minuto | ignorar pontuação, maiúsculas e números escritos × falados ("1936" × "mil novecentos e trinta e seis") |
| `pausas.py` | mapeia silêncios (tempos das palavras + `silencedetect`), encurta os longos, gera `narracao_vNN.wav` e a tabela de mudança de tempo | toda mudança de tempo vai para uma tabela original→novo; os tempos das palavras são convertidos por ela; fades de ~10 ms em cada emenda para não estalar |

Saída para o Claude ler: `_CLAUDE/transcricao/frases.md`, uma frase por linha, com o tempo (da narração ajustada), o capítulo e as pausas marcadas. O arquivo por palavra é só para os scripts.

## Passo a passo
1. Status e pendências desta etapa.
2. Ambiente (`scripts/instalar-local.sh`) em segundo plano, se faltar.
3. Inventário da narração. Mais de um arquivo (capítulos separados): pergunte a ordem e junte.
4. Alinhamento → conferência com o roteiro → mapa de pausas.
5. Mostre as divergências (se houver) e espere a decisão: gerar de novo com a `/video-narrar`, ou aceitar como está.
6. Ajuste das pausas → `narracao_v01.wav`.
7. **Entrega:** mande a narração ajustada pela conversa (é só áudio, leve) para ela ouvir o ritmo.

## Resumo no chat
Duração antes → depois, quantas pausas encurtadas, divergências com o roteiro (com minuto), tempos dos capítulos. Marque `aguardando_aprovacao`.

## Revisão
Ela pede por minuto ("no 2:10 a pausa ficou curta"). Ajustar só o citado, versão nova (`_v02`), anotar aprendizados no caderno (ex.: "pausas entre capítulos mais longas").

## Aprovação
Marque `concluido`. **A narração trava:** se mudar depois do mapa, avise que o mapa e as animações precisam ser recalculados. Diga quantos aprendizados ficaram anotados e sugira `/clear` e `/video`.

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar arquivos do projeto.
- Nunca trocar o que a voz falou pelo texto do roteiro.