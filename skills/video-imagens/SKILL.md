---
name: video-imagens
description: "Busca as fotos de arquivo, cartões-postais, jornais e vídeos que o mapa do vídeo do Rétrovisage pede, com fonte e licença, escolhendo sozinho a melhor opção de cada item para Isabella só conferir; depois prepara os recortes e as camadas. Use em /video-imagens, após a video-mapa, ou avulsa ('busca uma foto do metrô de Paris em 1920')."
---

# video-imagens

Junta as imagens reais que as cenas precisam e as prepara para a colagem (recorte, retícula, camadas). O que dá para desenhar em código (fitas, setas, mapas simples, molduras) não é desta etapa.

- **Lê:** bloco `cenas` (as imagens `imgNNN` e os vídeos `vidNNN` com descrição e termos de busca), `Imagens/`, perfil `identidade.md`
- **Escreve:** bloco `imagens` no estado; `_CLAUDE/imagens/` (originais baixados, recortes PNG, camadas); `_CLAUDE/creditos.json`
- **Próximo passo:** `/video-animar`

Se a `video-mapa` não estiver `concluido`, pare e sugira terminá-la.

## Busca automática (o caminho padrão, pedido por Isabella em 04/11)
O Claude **busca sozinho** fotos e vídeos, **escolhe a melhor opção** de cada item e mostra a folha numerada; Isabella **só avalia e aprova** ou troca por número.
- **APIs oficiais** (nunca raspar site nem burlar bloqueio de robô):
  | Fonte | Para | Acesso |
  |---|---|---|
  | ~~Pexels API~~ (`api.pexels.com`) — **emissão de chaves pausada pela Pexels em 04/11; sem chave por enquanto** | fotos e vídeos atuais, objetos, texturas | chave guardada como **Network secret** (cabeçalho `Authorization`, sem prefixo, site `api.pexels.com`): o proxy coloca a chave sozinho, não mandar cabeçalho de autorização no pedido; arquivos em `images.pexels.com` / `videos.pexels.com` |
  | **Pixabay API** (`pixabay.com/api/`, vídeos em `/api/videos/`) — **banco principal** | fotos e vídeos atuais | a chave vai na URL (`?key=`), então fica como **variável de ambiente** `PIXABAY_API_KEY`; nunca imprimir a URL com a chave; arquivos em `cdn.pixabay.com` |
  | Wikimedia Commons API | fotos de arquivo, época | sem chave; baixar **miniaturas** (`thumb.wikimedia.org`, até ~1920 px) com User-Agent identificado e pausa entre pedidos (originais em `upload.wikimedia.org` dão 429) |
  | **Archive.org** (coleção `prelinger`) | **filmes de época em domínio público** | sem chave; conferir a licença de cada item |
  | Library of Congress (`www.loc.gov`, `?fo=json`) | fotos de arquivo, muitas "no known restrictions" | sem chave |
  | Openverse (`api.openverse.org`) | agregador Creative Commons | sem chave; responde 504 no primeiro pedido às vezes, repetir |
  | ~~Gallica (BnF)~~ | — | **403 a acesso automatizado**, mesmo com User-Agent de navegador: não insistir |
  | ~~Europeana~~, ~~Smithsonian~~ | — | exigem chave; sem chave, não usar |
  | ~~Met Museum~~ | — | API desativada (410 Gone) |
- Chaves ficam no ambiente (Network secrets ou variável); nunca pedir para colar no chat. Teste rápido do Pexels: `curl -s -o /dev/null -w '%{http_code}' 'https://api.pexels.com/v1/search?query=ink&per_page=1'` → 200 = chave ok, 401 = segredo não configurado. Chave ausente ou domínio bloqueado: diga qual falta e peça para liberar (menu do ambiente → Edit → Network access); busque nos acervos que respondem e deixe os itens afetados como `a_buscar`. **Não** passar a busca para Isabella.
## Como buscar (aprendido errando em 20/11/2026, no retrovisage-03)

Use `ferramentas/video/buscar_midia.py` com um plano em JSON, e
`ferramentas/video/folha_contato.py` para a folha. Três regras que custaram três
rodadas perdidas:

1. **Pesquise o que a palavra significa no idioma da busca, antes de buscar.**
   `mold` é forma *e* mofo — trouxe morangos estragados para o item do aspic.
   `souffle` é o prato *e* o sopro. `jelly` é gelatina *e* água-viva. Por isso
   cada item do plano leva um campo `contexto` com palavras do domínio: sem uma
   delas nas tags, o candidato é descartado.
2. **Banco genérico não tem gesto, tem produto.** Buscar `mayonnaise` no Pixabay
   devolve hambúrguer e batata frita, corretamente etiquetados. O plano pedia o
   fouet deixando traços no bol — isso não existe lá. Para **gesto e época**, vá
   ao Archive.org e ao Commons; o Pixabay serve para plano moderno de objeto.
3. **Filme de arquivo não se cataloga por nome de prato.** `vol-au-vent` no
   Archive.org devolve nada ou desenho animado. Busque **tema e época, uma
   palavra forte**: `kitchen`, `gelatin`, `baking`, `dinner`, `recipe`, dentro
   de `collection:(prelinger)`. O título do filme quase nunca traz o tema, então
   a relevância é medida pelo assunto e pela descrição, não pelo nome.

Item sem o objeto exato fica **vazio e declarado na lista final** (decisão de
Isabella, 20/11/2026): folha com buraco é melhor que folha preenchida com o que
não é.

- **Escolha:** época certa (nada moderno onde a cena é 1960), objeto completo, boa resolução (vídeo ≥ 1280 px de largura), sem marca d'água, sem logo, sem rosto famoso. Preferir objeto isolado/fundo simples (recorta melhor).
- **Vídeo:** baixar a versão HD (não 4K: pesa no render), cortar o trecho útil (`ffmpeg`), guardar em `_CLAUDE/imagens/videos/vidNNN_v01.mp4`, sem áudio.
- **Folha de aprovação:** uma imagem com todos os itens; para cada um, a **escolha do Claude (1)** + 2 alternativas; vídeos aparecem como 3 quadros (começo, meio, fim). Isabella responde "tudo ok" ou "img07 2, vid03 busca outro".

## Caminho manual (só se Isabella pedir explicitamente; ela prefere tudo automático, 04/11)
Teste primeiro se os acervos respondem (ex.: `commons.wikimedia.org`, `upload.wikimedia.org`, `gallica.bnf.fr`, `api.europeana.eu`, `www.loc.gov`, `www.pexels.com`, `pixabay.com`).
- **A. Acervos liberados:** o Claude busca, baixa e mostra as opções.
- **B. Acervos bloqueados:** o Claude monta a **lista de busca**: para cada `imgNNN`, o que procurar, os termos em francês e inglês, os acervos indicados com o link de busca já pronto, e o **nome de arquivo esperado** (`img014.jpg`). Isabella baixa e sobe em `Imagens/`. Diga qual domínio liberar para o caminho A (regras comuns, seção 0).

## Fontes (pesquise o estado atual e as licenças antes de escrever o script)
| Acervo | Bom para | Licença |
|---|---|---|
| Gallica (BnF) | fotos de imprensa (Agence Rol, Meurisse), cartões-postais, jornais de época | ver a menção de cada documento; muitas em domínio público |
| Wikimedia Commons | fotos de arquivo francesas, Paris antiga | cada arquivo declara (PD, CC BY, CC BY-SA): anotar |
| Europeana | acervos europeus | cada item declara |
| Library of Congress | fotos da França (guerras, viagens) | muitas "no known restrictions" |
| Pexels / Pixabay | objetos, texturas, planos atuais "com cara de antigo", vídeos | licença própria, uso comercial livre, sem crédito obrigatório (registrar mesmo assim) |
| Archive.org | filmes de época (cuidado: muitos são americanos) | domínio público quando declarado |

## Licenças (firme)
- Sem licença clara, não entra: vira "Isabella manda" ou fica faltando.
- Foto francesa do século XX: domínio público só 70 anos após a morte do autor. Confiar no que o acervo declara e anotar.
- CC BY / CC BY-SA pedem crédito: tudo vai para `creditos.json` (título, autor, acervo, link, licença).

## Antes de buscar e ao preparar (aprendido em natal-1962)
- **Pesquisar o que o objeto citado é de verdade** antes de buscar. Ex.: *papillotes* são bombons de Natal em papel metalizado com franjas (não Papai Noel de chocolate, não barra embrulhada).
- **Objeto cortado pela borda da própria foto** (o triciclo com uma roda só) fica com cara de quebrado quando recortado: usar a foto inteira colada, ou pedir uma imagem do objeto completo.
- **Antes de espelhar** (`"espelhar": true`), conferir se o texto está espelhado ou só de cabeça para baixo (objeto segurado invertido). A img01 foi desvirada por engano.
- **Nunca usar imagem com marca d'água** (Pngtree e afins = prévia não licenciada). **Logotipo de marca** no objeto: recortar só o objeto, sem a marca.
- Objeto redondo no meio de vários (uma laranja num saco): modo `elipse`. Objeto de cor viva entre outros: modo `cor`.

## Como mostrar
- **Uma folha de contato numerada por rodada** (uma imagem só, opções lado a lado sobre o fundo do vídeo), nunca as opções soltas.
- Descarte antes o que está errado: época errada (carro moderno numa cena de 1930), lugar errado, marca d'água, resolução baixa demais (menos de ~800 px no lado menor para tela cheia).
- A recomendação é a opção 1. Ela responde por número ("img03 2, img07 eu mando").

## Preparar para a colagem (script `ferramentas/video/recortar.py`, escrito na primeira vez)
- **Recorte** do assunto (rembg, local) → PNG com transparência; borda branca fina ou rasgada no render.
- **Preto e branco com retícula** (perfil): no render, por CSS/filtro, não no arquivo (assim dá para ajustar).
- **Camadas para parallax** (frente, meio, fundo) nas cenas que pedem: recorte por camada + fundo com o buraco preenchido. Conferir a borda do recorte num quadro ampliado.
- Guarde o original sempre; o recorte é versão.

## Resumo no chat
O que entrou (id, fonte, licença), o que ficou faltando e o que **Isabella** precisa buscar ou subir, com o nome de arquivo esperado. O render constrói com um marcador visível no lugar do que faltar. Marque `aguardando_aprovacao`.

## Aprovação
Marque `concluido`. Pergunte se alguma imagem vai para uma biblioteca fixa (texturas, fundos, papéis que voltam em outros vídeos → `biblioteca/texturas/` no repositório do fluxo). `/clear` e `/video`.

## Regras comuns
Antes de começar, leia `.claude/skills/video/regras-comuns.md` (uma vez por sessão).

## Regras
- Nunca mover, renomear ou apagar o que Isabella subiu.
- Nunca usar imagem sem fonte e licença anotadas.