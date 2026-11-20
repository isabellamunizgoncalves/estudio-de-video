# Validação do estilo — Rétrovisage

## 2026-11-03 · cena de teste aprovada por Isabella (fda-2026-11-03-natal-1962-teste, cn01–cn03)
Confirmado:
- Fundo colorido com textura de papel (fibra + manchas, SVG turbulence) — verde #2E8B57.
- Foto de arquivo em P&B com borda branca 14 px, sombra 6/6/12 px 35%, leve retícula, inclinada (−2,5°).
- Entrada da foto deslizando da esquerda, 1,15 s, power3.out, já em movimento no 1º quadro.
- Objeto colorido (laranja) caindo com back.out(1.5), 0,5 s, como único elemento em cor.
- Círculo desenhado à mão (traço preto 9 px, 0,55 s power2.inOut).
- Troca por folha creme com borda rasgada atravessando a tela (0,7 s power3.inOut).
- Palavra-chave em Playfair Display 700, caixa vermelha crescendo da esquerda (0,3 s power3.out), texto claro sobre o vermelho (#FFF8EC, contraste ≥ 3:1).
- Câmera: aproximação (power1.out) + deriva linear em contêineres separados.
Técnico: HyperFrames 0.9.8, GSAP 3.15.0 local, fontes embutidas (pecas-base/), 1920x1080 30 qps; ~2 min de render para 8 s.