# Motor: Google AI Studio — A CONFIGURAR

Ainda **não está pronto para uso**. Este arquivo é o encaixe: quando as vozes do Google AI Studio
forem configuradas, preencha as seções abaixo e troque o estado na tabela do `SKILL.md`.
Enquanto isso, o motor padrão continua sendo o **Edge TTS** (`motores/edge.md`).

## O que falta decidir

- [ ] **Chave de API** — guardar como *network secret* do ambiente ou variável, nunca colada no chat
      nem commitada. Nunca imprimir a URL com a chave.
- [ ] **Voz** — qual voz francesa substitui ou acompanha a Remy, e em que casos usar cada uma.
- [ ] **Cota** — a camada gratuita tem limite diário baixo (indicações de ~15 pedidos/dia na pesquisa
      de 20/11/2026, não confirmado). Um roteiro inteiro é gerado parágrafo a parágrafo, ou seja,
      **dezenas de pedidos por vídeo**. Confirmar a cota real antes de adotar como padrão, e decidir
      se o roteiro vai em blocos maiores para caber.
- [ ] **Script** — `scripts/narrar_google.py`, com a mesma interface do `narrar_edge.py`:
      `--projeto`, `--voz`, `--rate`, `--pausa`, `--pausa-curta`, `--saida`.
- [ ] **Saída idêntica** — `Narracao/narracao_vNN.wav` + ficha `.json`. O contrato com a
      `/video-preparar` não muda, senão o resto do fluxo quebra.

## Privacidade

Motor em nuvem: o texto do roteiro sai da máquina, como no Edge TTS. Avisar nos mesmos casos.

## Comando

> A preencher quando o script existir.
