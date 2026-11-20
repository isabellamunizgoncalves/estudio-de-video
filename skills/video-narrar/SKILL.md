---
name: video-narrar
description: "Gera a narração do vídeo a partir do roteiro humanizado, parágrafo por parágrafo, com pausas que respeitam o texto. Motor padrão: Edge TTS (voz neural Remy, francês), rápido e sem GPU — ~4 min para 28 min de áudio. Use em /video-narrar, depois da video-iniciar, ou quando a pessoa pedir para narrar, gerar o áudio ou a voz de um roteiro."
---

# video-narrar

Transforma o roteiro humanizado em narração.

- **Lê:** `Roteiro/roteiro_humanizado.txt` (saída da `video-humanizar`), senão `Roteiro/roteiro.txt`
- **Escreve:** `Narracao/narracao_vNN.wav` (versão nova a cada geração, nunca sobrescreve)
  + a ficha `Narracao/narracao_vNN.json` (motor, voz, velocidade, pausas, duração)
- **Não mexe** no `_CLAUDE/projeto.json`: o estado da narração é da `/video-preparar`
- **Próximo passo:** `/video-preparar`

## Motores

A skill é a mesma para qualquer motor de voz. O que muda — comando, vozes, limites, privacidade —
fica em `motores/<motor>.md`. **Leia o arquivo do motor antes de gerar.**

| Motor | Arquivo | Estado |
|---|---|---|
| **Edge TTS** | `motores/edge.md` | **padrão** — voz `fr-FR-RemyMultilingualNeural` (Remy), escolhida em 19/11/2026 |
| Google AI Studio | `motores/google-ai-studio.md` | a configurar |

O motor vem de `_CLAUDE/projeto.json` (campo `motor_voz`), senão do perfil do canal, senão Edge.
Para trocar de motor num vídeo, ela pede explicitamente — e sai uma **versão nova**, a anterior fica.

**Motor novo:** escreva `motores/<nome>.md` seguindo o formato do `edge.md` (comando, vozes,
opções, privacidade, problemas comuns) e acrescente a linha na tabela acima. O resto da skill,
o contrato de arquivos e as etapas seguintes não mudam.

## Antes de gerar

1. **Vídeo:** `projects/<slug>/`. Se ela não disse qual, liste as pastas em `projects/` e pergunte.
2. **Texto:** se não houver `Roteiro/roteiro_humanizado.txt`, ofereça a `/video-humanizar` antes.
   Só use o `roteiro.txt` cru se ela preferir.
3. **Motor:** confirme qual é numa linha e leia `motores/<motor>.md`.
4. **Privacidade:** motores em nuvem mandam o texto do roteiro para fora da máquina. O arquivo do
   motor diz se é o caso. Ela já aceitou isso para o canal; avise de novo só se o texto tiver algo
   pessoal.

## Gerar

O comando está em `motores/<motor>.md`. Vale para todos:

- Rode **em segundo plano** para o roteiro inteiro: leva alguns minutos.
- **Teste um trecho antes** do roteiro inteiro: grave as primeiras linhas num `.txt` temporário e
  rode com a saída apontando para fora do projeto. Mande o áudio pela conversa para ela ouvir.

## Entrega

- Mande a narração pela conversa (ferramenta de envio de arquivo) e diga a duração.
- Avise o que a voz pode ler mal **sem mudar o texto**: algarismos (`25`, `1960`), numerais romanos
  (`Henri IV`), siglas. Se ela pedir, a correção é no roteiro humanizado (escrever por extenso) e
  gerar de novo.
- Divergência apontada depois pela `/video-preparar`: corrigir o texto se for o caso e gerar de novo;
  sai uma versão nova, a anterior fica.

## Regras

- Nunca mudar palavras do roteiro para "ajudar" a voz sem o "sim" dela.
- Nunca sobrescrever uma narração: sempre versão nova.
- Não clonar a voz de pessoas reais.
