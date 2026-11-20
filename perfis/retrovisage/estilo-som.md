# Estilo de som — Rétrovisage

Origem: referências analisadas em 2026-11-03 (analises/sintese.md) e escolhas da pessoa na montagem. Tendência, não regra.

## Efeitos
- **Poucos e discretos**: só em animações e viradas. (pedido em 2026-11-03)
- Combinam com papel e arquivo: papel rasgando, fita colando, página virando, whoosh suave, clique de máquina fotográfica antiga, máquina de escrever nas datas.
- Nível bem abaixo da voz, mas audível: no `mixar.py`, ~8–14 LU abaixo da voz (medido por RMS) funcionou em natal-1962 (03/11).
- **Papel ou jornal aparecendo na tela pede som de papel ou de folhear** (Isabella sentiu falta em natal-1962, cn16). Biblioteca: `biblioteca/sfx/papel/`.

## Música
- O Claude escolhe e encaixa (bancos gratuitos com licença clara; registrar crédito para a descrição).
- Clima: França de antigamente, leve e curiosa; pode mudar por capítulo.
- **Evitar acordeão/sanfona** (recusado em 03/11). Nostalgia: **piano** (ex.: *Gymnopédie No. 1*, Satie) ou caixinha de música. Viradas tensas/frias: **coral e violoncelos** (ex.: *Night Vigil*). Ambas aprovadas em natal-1962.
- **Música baixa: a voz sempre prevalece.** No `mixar.py`: `musica_abaixo_da_voz_lu` = 21, ducking razão 6, limiar 0,03, soltura 600 ms (aprovado em 03/11; 15 LU ficou alto).

## Aprovado em retrovisage02 (05/11)
- Uma faixa de piano por capítulo + **caixinha de música** no capítulo das brincadeiras; o **tema do começo volta no fim** (Gymnopédie no gancho e na conclusão).
- **Silêncio de propósito** nas viradas graves (Kennedy) e no "contraste moderno" (cena cinza): a música some e volta com a cor.
- ~1 efeito a cada 14 s (75 em 17 min), nunca o mesmo em menos de 20 s; carimbo em cada cartão N°, papel rasgando nas trocas, tilintar só nos brilhos. Níveis iguais aos de natal-1962 (música 21 LU abaixo, ducking 6:1).
- Antes de usar uma faixa, medir os silêncios internos (faixas muito rarefeitas não servem de fundo).