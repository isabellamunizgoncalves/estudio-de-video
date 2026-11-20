# Análise das referências — retrovisage

Analisado em 2026-11-03. Folhas de contato (2 qps) e folhas densas (15 qps) nesta pasta. Medição por quadro (contato), sem fluxo óptico ainda (OpenCV não instalado). Tendência, não regra.

| Ref | Arquivo | Formato |
|---|---|---|
| ref01 | How To Create VOX STYLE Animations FAST | 720x1280, 30 qps, 26 s |
| ref02 | How Vox makes images look like videos | 720x1280, 23,976 qps, 37 s |
| ref03 | The SECRET behind Vox's Editorial Style | 720x1280, 23,976 qps, 42 s |
| ref04 | VOX STYLE _ Atlantis | 720x1280, 30 qps, 52 s |

Todas são verticais (shorts); o canal é horizontal. Medimos o **jeito de mover**, não o desenho. Não usar logotipo, fontes de marca ou peças da Vox.

## Fichas

### ref01 — colagem de recortes
- Recortes em preto e branco com retícula (halftone) sobre fundos coloridos e texturizados; bordas de papel rasgado.
- Rótulos em fita (faixa amarela inclinada, letra condensada em caixa alta).
- Troca de fundo/cena a cada ~1,5 s (cortes em 0,7 · 2,2 · 3,7 · 4,4 · 6,0 s): ritmo de short, rápido demais para o canal.

### ref02 — foto que parece vídeo (parallax)
- Foto separada em 3 camadas (primeiro plano, meio, fundo) que andam em velocidades diferentes, com aproximação lenta. Entre 2 s e 5 s, o objeto do meio cresce ~10% de forma contínua, sem parar.
- Texto em serifa, com a palavra de destaque numa caixa vermelha por trás; setas desenhadas à mão apontando para o assunto.
- "Feito assim fica chato" (foto parada) vs. "assim fica vivo" (camadas): a ideia central da referência.

### ref03 — fundos em camadas
- Nunca fundo chapado: papel, recorte de jornal antigo, textura escura. Prédios e objetos recortados sobre esses fundos.
- Destaque por luz: vinheta clara em volta do assunto, holofote.
- Mãos recortadas "colocando" elementos na cena.

### ref04 — história narrada em colagem (a mais próxima do canal)
- Fundo de papel envelhecido creme/sépia o tempo todo; imagens em gravura P&B ou sépia com bordas rasgadas.
- **Entrada de rótulo** ("WHAT IF?"): cai do alto em ~8 quadros (0,20→0,47 s), chega inclinado e assenta; curva com leve passagem do ponto (tipo `back.out`).
- **Entrada de imagem**: desliza da esquerda em ~36 quadros (0,60→1,80 s), desacelerando no fim (tipo `power3.out`). Lenta, sem pressa.
- **Construção da cena**: a cada 1–2 s entra um elemento novo (imagem, rótulo de papel, mapa, bússola) até a cena "encher"; depois troca.
- **Trocas de cena** a cada ~5–7 s (8,5 · 13,2 · 17,0 · 24,0 · 29,5 · 36,1 · 41,4 · 48,1 s): papel que rasga, página que vira, cena que esvazia e enche de novo.
- **Rótulos** em tiras de papel ("2,000 YEARS AGO", "EARTHQUAKES", "NO PROOF") com letra condensada preta; um deles entra trazido por uma mão.
- Legenda palavra a palavra com destaque verde: recurso de short.

## Síntese (vira o perfil)
1. **Colagem de papel**: fundo de papel envelhecido, imagens recortadas com borda rasgada, rótulos em tira de papel. (refs 01, 03, 04)
2. **Nada fica parado**: toda foto tem movimento lento contínuo; nas fotos importantes, parallax em 2–3 camadas. (refs 02, 04)
3. **Entradas suaves e sem pressa**: imagens deslizam em ~1–1,2 s desacelerando (`power3.out`); rótulos caem em ~0,25–0,3 s com leve passagem do ponto (`back.out`). (ref04)
4. **Cena que se constrói**: um elemento novo a cada 1–2 s; troca de cena a cada 5–7 s. No vídeo longo, mais calmo no corpo. (ref04)
5. **Destaque**: palavra-chave em caixa colorida por trás, setas à mão, luz em volta do assunto. (refs 02, 03)

## Preferência da pessoa (2026-11-03)
- Prefere o estilo **colorido** das refs 01, 02 e 03. A ref04 (sépia, papel envelhecido) fica só como referência de ritmo de entrada e de construção de cena.
- Consequência: fundos vivos e texturizados (céu, padrões, cores chapadas com textura de papel), recortes P&B/retícula por cima. Contraste "foto de arquivo P&B × fundo colorido" é a assinatura.
- **Sem legenda** palavra a palavra, em nenhum trecho. Texto na tela só em poucos destaques (rótulos em fita, datas, palavra-chave com caixa).
