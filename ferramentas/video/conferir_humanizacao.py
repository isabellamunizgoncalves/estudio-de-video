#!/usr/bin/env python3
"""Confere que a humanização só mexeu em pontuação e quebras de linha.

Apaga pontuação, acentuação de caixa e quebras dos dois textos e compara as
sequências de palavras. Se diferirem, mostra onde. É o teste final da skill
video-humanizar: nenhuma palavra acrescentada, retirada, trocada ou reordenada.

Uso:
    python ferramentas/video/conferir_humanizacao.py original.txt humanizado.txt
    python ferramentas/video/conferir_humanizacao.py original.txt humanizado.txt --prefixo
"""
import re
import sys
import unicodedata


def palavras(caminho):
    txt = open(caminho, encoding="utf-8").read()
    txt = txt.replace("’", "'").replace("‘", "'")
    txt = unicodedata.normalize("NFC", txt)
    # tudo que não for letra, número ou apóstrofo vira separador
    cru = re.split(r"[^0-9A-Za-zÀ-ÿ'\-]+", txt.lower())
    return [p for p in cru if p]


def main():
    a, b = sys.argv[1], sys.argv[2]
    prefixo = "--prefixo" in sys.argv
    pa, pb = palavras(a), palavras(b)

    if prefixo:
        n = min(len(pa), len(pb))
        pa_cmp, pb_cmp = pa[:n], pb[:n]
    else:
        pa_cmp, pb_cmp = pa, pb

    if pa_cmp == pb_cmp:
        print(f"OK — {len(pb_cmp)} palavras idênticas"
              + (f" (prefixo; original tem {len(pa)}, humanizado {len(pb)})" if prefixo else ""))
        return 0

    for i, (x, y) in enumerate(zip(pa_cmp, pb_cmp)):
        if x != y:
            print(f"DIFERE na palavra {i + 1}:")
            print("  original :", " ".join(pa[max(0, i - 8):i + 8]))
            print("  humanizado:", " ".join(pb[max(0, i - 8):i + 8]))
            return 1
    print(f"DIFERE no tamanho: original {len(pa_cmp)}, humanizado {len(pb_cmp)}")
    extra = pb_cmp[len(pa_cmp):] or pa_cmp[len(pb_cmp):]
    print("  sobra:", " ".join(extra[:20]))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
