---
name: "video-humanizar"
description: "Use quando Isabella pedir para humanizar um roteiro para narração com voz de IA (TTS): deixa o texto fluido, com ritmo calmo e pausas que a voz respeita."
---

# Humanização de roteiro para narração com voz de IA

Objetivo: fazer com que uma voz de IA (ElevenLabs, CapCut, vidIQ etc.) leia o roteiro como um narrador humano que sente o que conta: que desacelera quando lembra, hesita quando se emociona, se anima quando surpreende e fica grave quando o assunto pesa. Não como alguém lendo uma lista. E tudo isso SEM mudar nenhuma palavra do texto.

O roteiro pode estar em qualquer idioma (francês, alemão, português...). O texto final fica sempre no idioma original do roteiro. As explicações para Isabella são em português do Brasil.

## REGRA NÚMERO UM: NÃO ALTERAR O CONTEÚDO EM HIPÓTESE ALGUMA

Isabella já escreveu e revisou o roteiro. Humanizar NÃO é reescrever. (Aprendido na prática: numa versão anterior foram acrescentadas frases como "Ferme les yeux un instant" e "Nous sommes le...", e isso estava errado.)

- Não acrescentar nenhuma palavra, frase, convite ao ouvinte, ambientação, ponte ou chamada.
- Não trocar, cortar nem reordenar palavras. Não trocar sinônimos, não "corrigir" o estilo (ex.: manter "Comment c'est possible ?", não mudar para "Comment est-ce possible ?").
- Não transformar fragmentos em frases completas com palavras novas, nem completar perguntas sem resposta.
- Não mudar maiúsculas de palavras escritas assim de propósito (ex.: manter "ABRI"). Se a voz puder soletrar, só avisar Isabella nas dicas finais.
- Algarismos, siglas ou palavras que a voz possa ler mal: não alterar; apenas avisar nas dicas finais e perguntar se ela quer que sejam escritos por extenso.
- Teste final: apagando toda a pontuação e as quebras de linha do original e da versão humanizada, as duas sequências de palavras têm de ser idênticas.

## O que é permitido mudar (e só isto)

1. **Pontuação:**
   - Trocar ponto final por vírgula ou dois-pontos para juntar frases picadas numa só respiração ("Une détonation énorme. Des vitres qui pleuvent. De la fumée..." → "Une détonation énorme, des vitres qui pleuvent, de la fumée...").
   - A letra inicial da palavra seguinte pode mudar de maiúscula para minúscula (ou o contrário) só por causa dessa troca de pontuação.
   - Acrescentar reticências em pontos de suspense ou hesitação, no máximo uma por parágrafo, nunca no meio de expressões. Usar o mesmo estilo de reticências do original (… ou ...).
   - Manter as aspas do original (« » no francês).
2. **Quebras de parágrafo (linha em branco = pausa longa):**
   - Isolar numa linha própria frases de impacto ("Retiens ce détail. Il va compter.", "C'était toi.").
   - Separar cada transição, cada mudança de emoção, cada marcador de seção ("Premier jour. Samedi.").
   - Dividir parágrafos longos em dois quando a emoção muda.

## Os dois erros de ritmo a evitar

1. **Texto picado.** Muitas frases curtas com ponto final em sequência fazem a voz parar seco e acelerar entre elas. Resolver trocando pontos por vírgulas.
2. **Texto corrido sem alma.** Tudo encadeado no mesmo ritmo deixa a narração plana. Resolver com linhas em branco e reticências nos momentos de emoção.

Regra prática: encadear com vírgulas nas partes informativas; abrir espaço (linhas em branco, reticências) nas partes emocionais. Nunca mais de duas frases curtas (menos de seis palavras) seguidas no mesmo parágrafo, exceto quando a frase curta fica sozinha num parágrafo próprio, de propósito.

## Passo 1: mapa emocional

Antes de mexer, ler o roteiro inteiro e decidir a emoção de cada bloco (abertura, cada parte, cada transição, fechamento). O contraste entre emoções é criado só com pontuação e pausas.

## Passo 2: emoção só pela pontuação e pelas pausas

- **Contemplação e nostalgia:** vírgulas para frases suaves, reticências antes da imagem principal, frase curta isolada para criar silêncio.
- **Reflexão e perguntas:** se a pergunta já tiver uma frase depois no original, manter no mesmo parágrafo para a voz não pular adiante.
- **Humor:** a graça no fim do parágrafo, com reticências antes se ajudar.
- **Suspense e tensão:** reticências antes da revelação, linha em branco, e a revelação no seu próprio parágrafo quando o original já a tiver como frase separada.
- **Gravidade e luto:** parágrafos curtos, linha em branco depois para o peso assentar.
- **Chamada à ação:** parágrafo próprio, sem pressa.

## Passo 3: a abertura é a parte mais lenta do vídeo

Nos primeiros 30 a 45 segundos, quebrar o texto em mais parágrafos que no resto do vídeo (um por imagem ou sensação), com pelo menos uma frase curta isolada, para a voz ir mais devagar. Sem acrescentar nenhuma frase.

## Nada que a voz leia por engano

No texto entregue: sem negrito, títulos com #, colchetes, parênteses de direção ("(pause)"), emojis, travessões longos ou barras. Se o original tiver algo assim, não remover por conta própria: avisar Isabella.

## Tags de emoção (opcional, só com autorização)

Algumas ferramentas aceitam marcações: no ElevenLabs, `<break time="1.0s" />` para pausas e, no modelo v3, tags como [whispers], [sighs], [excited], [laughs]. Só usar se Isabella pedir explicitamente. Sem confirmação, o texto precisa funcionar só com pontuação e quebras.

## Checagem antes de entregar

- Comparar palavra por palavra com o original: nenhuma palavra acrescentada, retirada, trocada ou reordenada?
- Cada frase cabe numa respiração?
- O ritmo varia entre partes informativas e emocionais?
- No máximo uma reticência por parágrafo?
- Nenhuma marcação nova dentro do texto narrado?

## Entrega

- O texto narrado, pronto para colar na ferramenta de voz: só o que deve ser falado, parágrafos separados por linha em branco.
- Se o roteiro é de um vídeo em `projects/<slug>/` (ex.: `Roteiro/roteiro.txt`), salvar em `projects/<slug>/Roteiro/roteiro_humanizado.txt`, sem tocar no original. É esse arquivo que a narração lê.
- Fora de um vídeo: se Isabella enviou o roteiro como arquivo .txt, devolver em .txt; se for longo e veio colado, entregar num documento; se for curto, na resposta.
- Próximo passo do fluxo: `/video-iniciar` (se o vídeo ainda não foi aberto) e a narração (`/video-narrar`).
- Depois do texto, no máximo 3 linhas em português: confirmar que só pontuação e quebras foram mexidas, avisar sobre palavras que a voz pode ler mal (maiúsculas, siglas, algarismos) sem alterá-las, e dicas de voz (velocidade por volta de 0,9, estabilidade média, mais expressividade se a ferramenta permitir).