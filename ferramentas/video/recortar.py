#!/usr/bin/env python3
"""Prepara as imagens para a colagem: corte, recorte do assunto (sem fundo) ou máscara em elipse.

Uso: .venv-edicao/bin/python -I recortar.py <pasta-do-video> <spec.json> [--so img02,img07]

spec.json: {"img02": {"modo": "elipse", "corte": [x0,y0,x1,y1], "elipse": [cx,cy,rx,ry]}, ...}
  - "corte": frações da imagem original (0–1). Tira bordas, marcas de acervo, chapas de vidro.
  - modo "quadro":  só corta. Sai PNG sem transparência (vira foto colada com borda no render).
  - modo "recorte": corta e tira o fundo (rembg, modelo isnet-general-use). Sai PNG com transparência,
                    aparado no assunto com uma margem pequena.
  - modo "elipse":  corta e aplica uma elipse suave (frações do corte). Para objetos redondos num grupo
                    (uma laranja entre várias), onde o rembg levaria os vizinhos junto.
  - "espelhar": true desvira a imagem. CUIDADO: confira antes se o texto está espelhado (letras ao contrário) ou só de cabeça para baixo (objeto segurado invertido) — neste caso NÃO espelhe.
  - "lado_max": maior lado da saída em px (padrão 2400; o render compõe em 1080p com folga para zoom).

Saída: _CLAUDE/imagens/prontas/<id>_v01.png (nunca sobrescreve: incrementa a versão).
O original em Imagens/ nunca é alterado. P&B e retícula são feitos no render (CSS), não aqui.
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def achar_original(pasta, ident):
    c = sorted(glob.glob(os.path.join(pasta, "Imagens", ident + ".*")))
    if not c:
        sys.exit(f"{ident}: arquivo não encontrado em Imagens/")
    return c[0]


def proxima_versao(dest, ident):
    v = 1
    while os.path.exists(os.path.join(dest, f"{ident}_v{v:02d}.png")):
        v += 1
    return os.path.join(dest, f"{ident}_v{v:02d}.png")


def limpar_ilhas(img, min_frac=0.02):
    """Tira pedaços soltos do recorte: mantém só as manchas com pelo menos min_frac da maior."""
    import cv2
    a = np.array(img.split()[-1])
    n, rot, stats, _ = cv2.connectedComponentsWithStats((a > 16).astype(np.uint8), connectivity=8)
    if n <= 2:
        return img
    areas = stats[1:, cv2.CC_STAT_AREA]
    manter = {i + 1 for i, ar in enumerate(areas) if ar >= areas.max() * min_frac}
    a = np.where(np.isin(rot, list(manter)), a, 0).astype(np.uint8)
    img.putalpha(Image.fromarray(a))
    return img


def aparar(img, margem=0.02):
    a = np.array(img.split()[-1])
    ys, xs = np.where(a > 16)
    if len(xs) == 0:
        return img
    m = int(max(img.size) * margem)
    return img.crop((max(0, xs.min() - m), max(0, ys.min() - m),
                     min(img.width, xs.max() + m), min(img.height, ys.max() + m)))


def main():
    pasta, spec_path = sys.argv[1], sys.argv[2]
    so = sys.argv[sys.argv.index("--so") + 1].split(",") if "--so" in sys.argv else None
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    dest = os.path.join(pasta, "_CLAUDE", "imagens", "prontas")
    os.makedirs(dest, exist_ok=True)
    sessao = None
    for ident, s in spec.items():
        if so and ident not in so:
            continue
        img = Image.open(achar_original(pasta, ident)).convert("RGB")
        x0, y0, x1, y1 = s.get("corte", [0, 0, 1, 1])
        img = img.crop((int(x0 * img.width), int(y0 * img.height), int(x1 * img.width), int(y1 * img.height)))
        if s.get("espelhar"):  # chapa de vidro impressa ao contrário: letras invertidas
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        lado = s.get("lado_max", 2400)
        if max(img.size) > lado:
            img.thumbnail((lado, lado), Image.LANCZOS)
        modo = s["modo"]
        if modo == "recorte":
            if sessao is None:
                from rembg import new_session
                sessao = new_session("isnet-general-use")
            from rembg import remove
            img = remove(img, session=sessao, post_process_mask=True)
            img = aparar(limpar_ilhas(img, s.get("ilha_min", 0.02)))
        elif modo == "elipse":
            cx, cy, rx, ry = s["elipse"]
            w, h = img.size
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).ellipse(((cx - rx) * w, (cy - ry) * h, (cx + rx) * w, (cy + ry) * h), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(max(w, h) * 0.004))
            img = img.convert("RGBA"); img.putalpha(mask)
            img = aparar(img, 0.01)
        elif modo == "cor":
            # Recorte por cor (HSV do OpenCV: matiz 0–180): separa um objeto de cor viva do que está
            # em volta (ex.: clementinas sem a mão nem a cesta). "hsv_min"/"hsv_max" = [H, S, V].
            import cv2
            hsv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2HSV)
            m = cv2.inRange(hsv, np.array(s.get("hsv_min", [8, 150, 110])), np.array(s.get("hsv_max", [26, 255, 255])))
            k = max(3, int(max(img.size) * 0.004) | 1)
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k * 3, k * 3), np.uint8))
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
            m = cv2.GaussianBlur(m, (k, k), 0)
            img = img.convert("RGBA"); img.putalpha(Image.fromarray(m))
            img = aparar(limpar_ilhas(img, s.get("ilha_min", 0.05)), 0.01)
        elif modo != "quadro":
            sys.exit(f"{ident}: modo desconhecido {modo}")
        saida = proxima_versao(dest, ident)
        img.save(saida, optimize=True)
        print(f"{ident}: {modo} -> {os.path.basename(saida)} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()