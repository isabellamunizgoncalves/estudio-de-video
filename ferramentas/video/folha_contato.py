#!/usr/bin/env python3
"""Monta a folha de contato numerada dos candidatos de imagem e vídeo.

Uma folha por rodada, nunca as opções soltas: cada item aparece com as suas
opções lado a lado, numeradas, para a pessoa responder por número
("img03 2, vid07 busca outro"). Vídeo aparece como 3 quadros (começo, meio, fim).

Uso:
    python ferramentas/video/folha_contato.py --projeto projects/retrovisage-03
    python ferramentas/video/folha_contato.py --projeto projects/retrovisage-03 --so vid01 vid02
    python ferramentas/video/folha_contato.py --projeto projects/retrovisage-03 --tipo foto

Lê:    <projeto>/_CLAUDE/imagens/busca/candidatos.json (saída do buscar_midia.py)
Grava: <projeto>/_CLAUDE/imagens/busca/folhas/folha_<tipo>_<n>.jpg
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CELULA = 320          # largura de cada opção, em pixels
MARGEM = 14
ALTURA_ROTULO = 26
FUNDO = (24, 22, 20)
TEXTO = (236, 232, 226)
APAGADO = (150, 144, 136)
POR_FOLHA = 6         # itens por folha


def _fonte(tam: int):
    for caminho in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(caminho, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def _quadros_video(video: Path, quantos: int = 3) -> list[Image.Image]:
    """Começo, meio e fim do trecho — mostra o movimento, não só um frame."""
    dur = 5.0
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True)
        dur = float(r.stdout.strip()) or 5.0
    except (ValueError, OSError):
        pass

    quadros = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(quantos):
            t = dur * (0.08 + 0.84 * i / max(1, quantos - 1))
            alvo = Path(tmp) / f"q{i}.jpg"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}",
                            "-i", str(video), "-frames:v", "1", str(alvo)],
                           capture_output=True)
            if alvo.exists():
                quadros.append(Image.open(alvo).convert("RGB").copy())
    return quadros


def _miniatura(img: Image.Image, larg: int) -> Image.Image:
    alt = max(1, round(img.height * larg / img.width))
    return img.resize((larg, alt), Image.LANCZOS)


def _linha_item(idn: str, item: list[dict], projeto: Path, fonte, fonte_p) -> Image.Image | None:
    """Uma faixa horizontal: rótulo + as opções numeradas do item."""
    blocos: list[tuple[Image.Image, str]] = []
    for n, cand in enumerate(item, 1):
        arq = projeto / cand["arquivo"]
        if not arq.exists():
            continue
        try:
            if arq.suffix.lower() == ".mp4":
                quadros = _quadros_video(arq)
                if not quadros:
                    continue
                larg = (CELULA - 2 * len(quadros)) // len(quadros)
                minis = [_miniatura(q, larg) for q in quadros]
                alt = max(m.height for m in minis)
                tira = Image.new("RGB", (CELULA, alt), FUNDO)
                x = 0
                for m in minis:
                    tira.paste(m, (x, 0)); x += m.width + 2
                blocos.append((tira, f"{n}. {cand['acervo']}"))
            else:
                blocos.append((_miniatura(Image.open(arq).convert("RGB"), CELULA),
                               f"{n}. {cand['acervo']}"))
        except Exception:
            continue

    if not blocos:
        return None

    alt_img = max(b[0].height for b in blocos)
    larg = MARGEM + len(blocos) * (CELULA + MARGEM)
    faixa = Image.new("RGB", (larg, ALTURA_ROTULO + alt_img + ALTURA_ROTULO), FUNDO)
    d = ImageDraw.Draw(faixa)
    d.text((MARGEM, 5), idn, font=fonte, fill=TEXTO)

    x = MARGEM
    for img, rotulo in blocos:
        faixa.paste(img, (x, ALTURA_ROTULO))
        d.text((x, ALTURA_ROTULO + alt_img + 5), rotulo, font=fonte_p, fill=APAGADO)
        x += CELULA + MARGEM
    return faixa


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True, type=Path)
    ap.add_argument("--so", nargs="*", help="só estes ids")
    ap.add_argument("--tipo", choices=["video", "foto"], help="só vídeos ou só fotos")
    ap.add_argument("--por-folha", type=int, default=POR_FOLHA)
    args = ap.parse_args()

    busca = args.projeto / "_CLAUDE" / "imagens" / "busca"
    registro = json.loads((busca / "candidatos.json").read_text(encoding="utf-8"))
    destino = busca / "folhas"
    destino.mkdir(parents=True, exist_ok=True)

    ids = [k for k, v in registro.items() if v]
    if args.so:
        ids = [i for i in ids if i in args.so]
    if args.tipo:
        ids = [i for i in ids if i.startswith("vid" if args.tipo == "video" else "img")]
    if not ids:
        print("nada para montar"); return 1

    fonte, fonte_p = _fonte(19), _fonte(14)
    geradas = []
    for n in range(0, len(ids), args.por_folha):
        lote = ids[n: n + args.por_folha]
        faixas = [f for f in (_linha_item(i, registro[i], args.projeto, fonte, fonte_p)
                              for i in lote) if f]
        if not faixas:
            continue
        larg = max(f.width for f in faixas)
        folha = Image.new("RGB", (larg, sum(f.height for f in faixas) + MARGEM), FUNDO)
        y = 0
        for f in faixas:
            folha.paste(f, (0, y)); y += f.height
        rotulo = args.tipo or "tudo"
        alvo = destino / f"folha_{rotulo}_{n // args.por_folha + 1}.jpg"
        folha.save(alvo, quality=88)
        geradas.append(alvo)
        print(f"{alvo}  ({', '.join(lote)})")

    print(f"\n{len(geradas)} folha(s) em {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
