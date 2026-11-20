# Montagem do fluxo de edição

Fase atual: 7 — **MONTAGEM CONCLUÍDA** · Atualizado em 2026-11-03

## Onde a montagem acontece
- Feita numa sessão do Claude Code na nuvem (ambiente temporário). Tudo fica neste repositório: isabellamunizgoncalves/meu-fluxo-de-edicao.
- O fluxo roda na nuvem (o PC de Isabella é fraco). Cada sessão nova: abrir este repositório; o ambiente Python é recriado por `ferramentas/instalar.sh`.

## Ambiente (nuvem, só referência)
- Sistema: Linux · Python: 3.13 · FFmpeg: 6.1 · Node.js: 22 · Git: sim · GPU: não
- Instalado (recriável por `ferramentas/instalar.sh`): faster-whisper large-v3 (CPU), rembg (isnet), OpenCV, NumPy, soundfile, PySceneDetect. HyperFrames 0.9.8 via npx; GSAP 3.15.0 e fontes locais em `perfis/retrovisage/pecas-base/`.

## Decisões
- Revisão: vídeo pronto (sem programa). A pessoa assiste e pede ajustes pelo chat; renders enviados pela conversa. PC dela é fraco: todo o trabalho pesado roda na nuvem.
- Tipo e formato: vídeo narrado (voz sobre imagens, vídeos e fotos), horizontal 16:9. Duração 10–20 min (trabalhar por trecho). 1920x1080, 30 fps (padrão sugerido, sem objeção).
- Narração: voz gerada por IA a partir do roteiro feita no DarkPlanner pela pessoa; ela manda o áudio exportado (mp3/wav). Roteiro sempre fornecido.
- Imagens/vídeos/fotos: o Claude busca (bancos com licença clara) ou sugere o que buscar; a pessoa sobe no GitHub.
- Pastas: ferramentas, skills e perfil num repositório GitHub da pessoa (usuário isabellamunizgoncalves; sugestão: privado `meu-fluxo-de-edicao`), baixado a cada sessão. Projeto: a decidir.
- Entrada de mídia: Drive compartilhado por link. Pendente: liberar drive.google.com e drive.usercontent.google.com na rede do ambiente (bloqueados no teste).
- Transcrição: alinhamento do áudio com o roteiro (tempo por palavra). Sugestão: WhisperX na CPU da nuvem, com o roteiro como referência de grafia. Conferir trechos com som e sem palavra.
- Notas faladas: não se aplica (voz por IA). Instruções de edição vão no roteiro.
- Canal: histórias do cotidiano da França no século XX.
- Animação: moderada. Forte no gancho, depois só ênfases (datas, nomes, lugares, números, viradas). Textos na tela, mapas, linhas do tempo, telas de capítulo. Ferramenta: HyperFrames (a confirmar instalação na nuvem).
- Fontes de imagem: acervos de arquivo (Gallica/BnF, Wikimedia Commons, Europeana, Library of Congress, Archives nationales) + bancos gratuitos para planos genéricos. Cuidado: foto francesa do séc. XX nem sempre é domínio público (autor morto há menos de 70 anos). Registrar a fonte e a licença de cada imagem.
- Câmera: movimento lento (zoom/deslize) em todas as fotos; detalhes do estilo no perfil.
- Som: efeitos poucos e discretos (só em animações e viradas). Música: o Claude escolhe e encaixa (bancos gratuitos de licença clara: Pixabay Music, Free Music Archive, Incompetech/CC-BY; registrar licença e crédito), volume baixo sob a voz, clima muda por capítulo. Biblioteca de sons/músicas fica no repositório (ou Drive) e cresce a cada vídeo.
- Revisões: plano de imagens/animações pelo chat (lista numerada); primeiro vídeo visual assistindo, por trecho; vídeo final com som assistindo, inteiro. Correções citando minuto ou número do item.
- Nomes: prefixo `rv-`; skill mestra `/video` (sugestão aceita).
- Projeto: um repositório de mídia por vídeo (`AAAA-MM-DD_Nome`: `Roteiro/`, `Narracao/`, `Imagens/`, `Musica/`, `Renders/`, `_CLAUDE/`). Ferramentas/skills/perfil no repositório `meu-fluxo-de-edicao`.

## Perfil
- retrovisage (canal Rétrovisage): identidade, estilo-motion, estilo-camera, estilo-cortes, estilo-som e catálogo escritos a partir de 4 refs (01–03 preferidas, coloridas). Sem legenda. Falta: confirmar níveis de som e ar entre frases no primeiro vídeo.

## Fluxo aprovado
1. video-iniciar — repositório do vídeo, roteiro, briefing, gancho e capítulos.
2. video-preparar — narração: alinhamento por palavra, conferência com o roteiro, pausas (inclui a etapa de cortes).
3. video-mapa — plano cena a cena (imagem, colagem, texto, movimento); aprovação pelo chat.
4. video-imagens — busca (ou lista de sugestões) com licença; recortes e camadas.
5. video-animar — colagens animadas no HyperFrames, com o movimento (inclui a etapa de câmera); render por trecho.
6. video-som — música por capítulo e poucos efeitos discretos; mix.
7. video-final — vídeo final 1080p, créditos e capítulos para o YouTube.
Mais: /video (skill mestra) e regras comuns.

## Skills escritas (em .claude/skills/)
- [x] regras comuns (editar/regras-comuns.md)
- [x] editar (skill mestra)
- [x] video-iniciar · [x] video-preparar · [x] video-mapa · [x] video-imagens · [x] video-animar · [x] video-som · [x] video-final
- Scripts testados no vídeo de teste: estado.py, instalar.sh, alinhar.py, conferir_roteiro.py, pausas.py, recortar.py, montar_html.py, mixar.py, sintetizar_sfx.py, final.py.

## Rede (domínios a liberar no ambiente)
- Mídia de entrada (opcional): drive.google.com, drive.usercontent.google.com
- Imagens: commons.wikimedia.org, upload.wikimedia.org, gallica.bnf.fr, api.europeana.eu, www.europeana.eu, www.loc.gov, tile.loc.gov, www.pexels.com, images.pexels.com, pixabay.com, cdn.pixabay.com
- Música: freemusicarchive.org, incompetech.com (Pixabay já acima)
- Ferramentas: download.pytorch.org (PyTorch CPU)
- Já funcionam: pypi.org, registry.npmjs.org, huggingface.co, fonts.googleapis.com

## Teste (fase 6)
- Vídeo: fda-2026-11-03-natal-1962-teste (49 s). Todas as etapas concluídas; final v02 aprovado.
- Backup do projeto do vídeo no ramo `backup/fda-2026-11-03-natal-1962-teste` (o repositório do vídeo não foi criado).
- 15 aprendizados anotados em `_CLAUDE/aprendizados.md` do vídeo, a aplicar com `/video aprendizados`.
- Rede: imagens/sons do Wikimedia exigem `thumb.wikimedia.org` liberado; Pixabay e Freesound bloqueiam automação; Incompetech funciona.

## Próximo passo
Montagem concluída. Para um vídeo novo: `/video` (ou `/video-iniciar`). Para melhorar o fluxo: `/video aprendizados`. Para mudar o fluxo: `/fluxo-de-edicao`.