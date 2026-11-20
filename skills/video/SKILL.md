---
name: video
description: "Ponto de entrada do estúdio: mostra em que etapa cada vídeo está (roteiro, narração, edição), com pendências, alertas e aprendizados anotados, e abre a skill da etapa certa. Também aplica os aprendizados (/video aprendizados). Use em /video, ao abrir ou retomar um vídeo, depois de um /clear, ou quando a pessoa perguntar em que pé está o vídeo."
---

# video

A cadeia inteira, do tema ao arquivo final:

```
/video-roteiro → /video-humanizar → /video-iniciar → /video-narrar → /video-preparar
→ /video-mapa → /video-imagens → /video-animar → /video-som → /video-final
```

Antes de tudo, leia `regras-comuns.md` (nesta pasta), uma vez por sessão. A seção 0 diz onde tudo
mora e o que fazer no começo da sessão.

## /video

1. **Qual vídeo:** liste as pastas em `projects/` (menos `_templates`). Nenhuma: pergunte se é um
   vídeo novo e ofereça a `/video-roteiro` (tem roteiro para escrever) ou a `/video-iniciar` (o
   roteiro já existe). Mais de uma e ela não disse qual: pergunte, mostrando primeiro as que têm
   etapa em andamento.
2. **Antes da edição:** a pasta existe mas não tem `_CLAUDE/projeto.json`? O vídeo ainda não foi
   iniciado. Veja o que há em `Roteiro/`:
   - vazio → `/video-roteiro`
   - só `roteiro.md`/`roteiro.txt` → `/video-humanizar`
   - já tem `roteiro_humanizado.txt` → `/video-iniciar`
3. **Depois da `/video-iniciar`:** `Narracao/` vazia? O próximo passo é a narração (`/video-narrar`,
   ou ela sobe um `.wav` gerado em outra ferramenta).
4. **Status:** rode `ferramentas/util/estado.py projects/<slug> status` e mostre de forma curta:
   etapas, o que já foi feito por trecho, pendências, alertas e quantos aprendizados estão anotados.
5. **Próximo passo:** diga qual é e pergunte se segue. Com o "sim", abra a skill da etapa e siga as
   instruções dela.
   - Etapa aguardando revisão: o próximo passo é continuar essa mesma etapa, nunca pular.
   - Alerta de algo desatualizado (ex.: a narração mudou depois do mapa): mostre primeiro e espere
     a decisão dela.
   - Ela pediu outra etapa ou um trecho ("sim, só o gancho"): abra essa etapa e passe o trecho.
6. **Uma etapa por vez.** Não encadear etapas sozinho e não dar `/clear` (isso é sempre dela).
7. **Modelo:** lembre, numa linha, o modelo sugerido para a etapa (regras comuns, seção 8).

## /video aprendizados

Siga a seção 5 das regras comuns.

## Canal novo

Para montar o fluxo de edição de um canal **novo** — outro estilo, outro formato, outro idioma —
a skill é a `/fluxo-de-edicao`: ela entrevista você e escreve as skills e o perfil daquele canal.
Esta aqui só conduz vídeos de canais que já existem em `perfis/`.

## Regras

- Não editar vídeo nem rodar scripts de etapa: isso é das skills de cada etapa.
- Nunca mover, renomear ou apagar arquivos do projeto.
