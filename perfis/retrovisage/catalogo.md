# Catálogo de padrões — Rétrovisage

Repertório, nunca obrigação. Cresce com os vídeos aprovados.

- **Recorte + fundo vivo**: foto de arquivo P&B recortada desliza sobre fundo azul/vermelho/verde texturizado. (refs 01, 03)
- **Rótulo em fita**: data/lugar em Anton numa fita amarela que cai e assenta. (refs 01, 04)
- **Palavra com caixa**: frase em Playfair, palavra-chave com caixa vermelha crescendo por trás. (ref02)
- **Foto viva**: foto separada em 3 camadas com parallax. (ref02)
- **Cena que enche**: elementos entrando um a um até a colagem completar. (ref04)
- **Recorte de jornal**: manchete de época sobre fundo colorido, aproximação lenta. (ref03)

## Aprovados em fda-2026-11-03-natal-1962-teste (03/11)
- **Objeto-fio colorido**: um objeto em cor (a laranja) atravessa o vídeo e amarra a história; ecos depois (a clementina). (cn01, cn06, cn07, cn11)
- **Fita arrancada**: a fita antiga é arrancada e a nova bate por cima quando a data muda ("SÉCULO XIX" → "ANOS 1950"). (cn04–05)
- **Grupo que se recentraliza**: recortes entram um a um no ritmo dos números ditos e o grupo desliza para continuar centrado. (cn08)
- **Fita grande que bate** com o grupo tremendo no impacto. (cn09)
- **Guirlanda que acende** lâmpada por lâmpada sobre a foto. (cn11)
- **A cor escoa**: na virada dramática, a cena perde a cor, esfria e a câmera quase para; a geada cobre a tela para a troca. (cn12–13)
- **Mapa que congela**: contorno da França desenhado, a **bandeira se pinta faixa por faixa** dentro dele e a geada (véu translúcido com cristais) cobre de cima a baixo; título por baixo. (cn15)
- **Pilha de arquivo + carimbo**: folhas e jornal caem um sobre o outro, carimbo laranja bate no fim. (cn16)
- **Raios de sol** (motivo do logo) atrás do objeto-herói. (cn06, cn11)

## Aprovados em fda-2026-11-04-retrovisage02 (gancho, 04/11)
Peças-base prontas: `pecas-base/pecas.css` (visual) + `pecas-base/js/pecas.js` (movimento, `window.RV`).
- **Polaroides + contador**: fotos em polaroide caem em arco, acelerando, e o número no selo creme sobe junto até chegar **no número dito** (punch no fim). `RV.polaroides` (cn010)
- **Mancha de tinta**: gota violeta cai, se espalha e toma a tela; a cena nova se abre de dentro dela (clipPath `circle` crescendo, a borda violeta aparece como um anel). Objeto-fio do vídeo da escola (encre violette). `RV.mancha` (cn005→006, cn007→008)
- **Pálpebras**: os olhos fecham e abrem com uma piscada, para um "fechem os olhos" / volta ao passado. `RV.palpebras` (cn001–002)
- **Relógio que volta no tempo**: relógio de escola desenhado; os ponteiros giram para trás e travam na hora da história. `RV.relogio` + `RV.ponteirosVoltam` (cn002)
- **Folha rasgada**: folha de cor cheia com borda rasgada atravessa a tela (da direita ou subindo) e vira o fundo da cena seguinte. `RV.folhaRasgada` (cn003→004, cn013→014)
- **Tudo cai de uma vez**: recuo lento a partir de um objeto; na expressão "de uma vez" os recortes caem um atrás do outro (3–10 quadros de intervalo) e a colagem treme. (cn007)
- **Mergulho na imagem**: a câmera acelera para dentro de um quadro ou objeto (power4.in / power3.in) até a imagem tomar a tela; corte para a cena seguinte. (cn006, cn014)