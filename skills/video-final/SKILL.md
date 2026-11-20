---
name: video-final
description: "Junta as animações, a narração, a música e os efeitos do vídeo do Rétrovisage e gera o vídeo final em 1080p para o YouTube, com o texto de créditos para a descrição. Use em /video-final, após a video-som."
---

# video-final

Monta o vídeo final e entrega. Não cria animação nem escolhe som: só junta o que já foi aprovado.

- **Lê:** blocos `renders`, `narracao`, `musica`, `sfx`; `_CLAUDE/som/mix_vNN.wav`; `_CLAUDE/creditos.json`
- **Escreve:** `_CLAUDE/renders/final/<projeto>_final_vNN.mp4`; `_CLAUDE/entrega/creditos-descricao.txt`; `_CLAUDE/entrega/capitulos-youtube.txt`
- **Próximo passo:** vídeo publicado; `/video aprendizados` quando ela quiser

Se a `video-som` não estiver `concluido`, pare e sugira terminá-la.

## Montagem (FFmpeg, script `ferramentas/audio/final.py`, escrito na primeira vez)
- Junta os renders dos trechos na ordem, sem quadro duplicado ou faltando nas emendas (conferir a contagem de quadros total × duração da narração).
- Áudio: o mix aprovado. Alvo de loudness para YouTube ~ -14 LUFS integrado, pico verdadeiro ≤ -1 dBTP.
- Vídeo: H.264, 1920x1080, 30 qps constante, `yuv420p`, qualidade alta (CRF ~18), `+faststart`. Áudio AAC 48 kHz estéreo, 320 kbps.
- **Se a sessão caiu** e os renders sumiram: refaça os trechos pela `video-animar` a partir dos projetos salvos (mesma versão do HyperFrames do estado), sem mudar nada.

## Conferir antes de entregar
- Duração do vídeo = duração da narração ajustada (± 1 quadro).
- A voz em sincronia no começo, no meio e no fim (extrair 3 quadros com as palavras-gatilho).
- Nenhum marcador de "IMAGEM FALTANDO" no vídeo (procurar no estado).
- Loudness medida.

## Entrega
- Mande o MP4 pela conversa. Se for grande demais para o envio, gere também uma versão de revisão 720p e explique como baixar o final.
- **Créditos para a descrição** (`creditos-descricao.txt`): imagens, músicas e efeitos com autor, acervo e licença, no formato que cada licença pede.
- **Capítulos do YouTube** (`capitulos-youtube.txt`): `00:00 Título`, um por capítulo, pelos tempos reais.
- Lembrete curto: conferir a licença das imagens marcadas "a verificar", se houver.

## Resumo no chat
Duração, tamanho do arquivo, loudness, os dois textos prontos para colar. Marque `aguardando_aprovacao`.

## Revisão
Ela assiste ao vídeo inteiro e pede por minuto. Ajuste de animação volta para a `video-animar` só no trecho citado; de som, para a `video-som`. Depois, nova versão final (`_v02`). Anotar aprendizados.

## Aprovação
`concluido`. Diga quantos aprendizados estão anotados no caderno e sugira, quando ela quiser, `/video aprendizados` para o próximo vídeo sair melhor.

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca sobrescrever um vídeo final entregue: versão nova.
- Nunca mover, renomear ou apagar arquivos do projeto.