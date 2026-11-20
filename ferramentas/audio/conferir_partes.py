#!/usr/bin/env python3
"""Confere narração gerada em partes: transcreve cada áudio e compara com o texto da mesma parte.

Uso: .venv-edicao/bin/python -I conferir_partes.py <pasta-do-video> <pasta-audios> <pasta-textos> [--idioma fr]

Pareia <pasta-audios>/NOME.mp3 com <pasta-textos>/NOME.txt (ex.: lembranca07.mp3 ↔ lembranca07.txt).
Gera <pasta-do-video>/_CLAUDE/transcricao/partes/NOME.json (palavras com tempo, relativo à parte)
e imprime, por parte, as divergências reais (homófonos e grafia ignorados), com o tempo dentro da parte.
O modelo é carregado uma vez só.
"""
import difflib
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import alinhar  # noqa: E402
import conferir_roteiro as cr  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402


def comparar(texto, palavras):
    rt, rt_src = [], []
    escritas = texto.split()
    for i, w in enumerate(escritas):
        for t in cr.tokens_norm(w):
            rt.append(t); rt_src.append(i)
    ft, ft_src = [], []
    for i, p in enumerate(palavras):
        for t in cr.tokens_norm(p["w"]):
            ft.append(t); ft_src.append(i)
    sm = difflib.SequenceMatcher(a=rt, b=ft, autojunk=False)
    div = []
    for tag, a1, a2, b1, b2 in sm.get_opcodes():
        if tag == "equal":
            continue
        falado = " ".join(palavras[i]["w"] for i in sorted(set(ft_src[b1:b2])))
        escrito = " ".join(escritas[i] for i in sorted(set(rt_src[a1:a2])))
        if tag == "replace" and (cr.so_grafia(escrito, falado) or cr.fonetico_fr(escrito) == cr.fonetico_fr(falado)):
            continue
        idx = sorted(set(ft_src[b1:b2]))
        pmin = min((palavras[i]["p"] for i in idx), default=1.0)
        t = palavras[ft_src[b1]]["ini"] if b1 < b2 else (palavras[ft_src[b1 - 1]]["fim"] if b1 > 0 else 0)
        div.append({"tipo": {"replace": "trocada", "delete": "faltou", "insert": "a mais"}[tag],
                    "roteiro": escrito, "falado": falado, "tempo": round(t, 2), "p_min": round(pmin, 2)})
    return div


def main():
    pasta, pa, pt = sys.argv[1:4]
    cr.IDIOMA = alinhar.IDIOMA = sys.argv[sys.argv.index("--idioma") + 1] if "--idioma" in sys.argv else "fr"
    dest = os.path.join(pasta, "_CLAUDE", "transcricao", "partes"); os.makedirs(dest, exist_ok=True)
    modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
    resumo = {}
    for audio in sorted(glob.glob(os.path.join(pa, "*.mp3"))):
        nome = os.path.splitext(os.path.basename(audio))[0]
        txt = os.path.join(pt, nome + ".txt")
        if not os.path.exists(txt):
            print(f"{nome}: sem texto correspondente"); continue
        wav = os.path.join(dest, nome + "_16k.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ac", "1", "-ar", "16000", wav], check=True)
        palavras = alinhar.transcrever(modelo, wav)
        os.remove(wav)
        json.dump(palavras, open(os.path.join(dest, nome + ".json"), "w"), ensure_ascii=False, indent=0)
        div = comparar(open(txt, encoding="utf-8").read(), palavras)
        resumo[nome] = div
        print(f"== {nome}: {len(div)} divergência(s)", flush=True)
        for d in div:
            print(f"   {int(d['tempo'] // 60)}:{d['tempo'] % 60:05.2f} {d['tipo']} (p {d['p_min']}): "
                  f"roteiro «{d['roteiro']}» / voz «{d['falado']}»", flush=True)
    json.dump(resumo, open(os.path.join(dest, "divergencias.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()