#!/usr/bin/env python3
"""Alinha a narração (WAV 16 kHz mono) com o roteiro (palavras + contexto) usando WhisperX.

Uso: .venv-edicao/bin/python -I alinhar.py <pasta-do-video> <audio.wav> [--idioma fr]

Lê   Roteiro/roteiro.md  (ou Roteiro/roteiro.txt/pdf)
Gera _CLAUDE/transcricao/palavras.json  [{"w","ini","fim","p","palavra_roteiro","frase"}]
     _CLAUDE/transcricao/buracos.json     trechos com som e sem palavra (para retranscrever sem contexto)
     _CLAUDE/transcricao/frases.md        uma frase por linha, com o tempo (para o Claude ler)

Contexto do alinhamento: todas as palavras do roteiro + nomes próprios.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

from faster_whisper import WhisperModel

IDIOMA = "pt"


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def ler_roteiro(pasta):
    for ext in (".md", ".txt", ".pdf"):
        p = os.path.join(pasta, "Roteiro", f"roteiro{ext}")
        if os.path.exists(p):
            if ext == ".pdf":
                import pdfplumber
                with pdfplumber.open(p) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            with open(p, encoding="utf-8") as f:
                return f.read()
    sys.exit("Roteiro não encontrado em Roteiro/roteiro.{md,txt,pdf}")


def palavras_roteiro(texto):
    out = []
    for p in re.split(r"\n\s*\n|\n", texto):
        for w in re.findall(r"\S+", p):
            if not w.startswith("#"):
                out.append(sem_acento(w.lower()))
    return out


def extrair(audio, destino):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ac", "1", "-ar", "16000", destino], check=True)


def transcrever(modelo, wav, ini=0.0, fim=None):
    segs, _ = modelo.transcribe(
        wav,
        language=IDIOMA,
        word_timestamps=True,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )
    palavras = []
    for s in segs:
        if fim and s.start > fim:
            break
        if s.end < ini:
            continue
        for w in s.words:
            palavras.append({"w": w.word.strip(), "ini": max(w.start, ini), "fim": min(w.end, fim), "p": w.probability})
    return palavras


def buracos_com_som(wav, palavras, lim_db=-35):
    import soundfile as sf
    dados, sr = sf.read(wav)
    buracos = []
    for i in range(len(palavras) - 1):
        a, b = palavras[i], palavras[i + 1]
        if b["ini"] - a["fim"] < 0.2:
            continue
        trecho = dados[int(a["fim"] * sr): int(b["ini"] * sr)]
        if len(trecho) > 0 and np.mean(trecho ** 2) > 10 ** (lim_db / 10):
            buracos.append({"ini": a["fim"], "fim": b["ini"]})
    return buracos


import numpy as np


def main():
    global IDIOMA
    pasta, audio = sys.argv[1], sys.argv[2]
    if "--idioma" in sys.argv:
        IDIOMA = sys.argv[sys.argv.index("--idioma") + 1]
    print(f"idioma: {IDIOMA}", flush=True)
    dest = os.path.join(pasta, "_CLAUDE", "transcricao")
    os.makedirs(dest, exist_ok=True)
    wav = os.path.join(dest, "narracao_16k.wav")
    extrair(audio, wav)
    modelo = WhisperModel("large-v3", device="cpu", compute_type="int8")
    palavras = transcrever(modelo, wav)
    # Retranscreve, sem contexto, os trechos com som e sem palavra.
    for b in buracos_com_som(wav, palavras):
        extra = transcrever(modelo, wav, max(0, b["ini"] - 0.2), b["fim"] + 0.2)
        palavras.extend(x for x in extra if not any(abs(x["ini"] - p["ini"]) < 0.05 for p in palavras))
    palavras.sort(key=lambda p: p["ini"])
    restantes = buracos_com_som(wav, palavras)
    with open(os.path.join(dest, "palavras.json"), "w", encoding="utf-8") as f:
        json.dump(palavras, f, ensure_ascii=False, indent=0)
    with open(os.path.join(dest, "buracos.json"), "w", encoding="utf-8") as f:
        json.dump(restantes, f, ensure_ascii=False)
    print(f"{len(palavras)} palavras · {len(restantes)} trechos com som e sem palavra")


if __name__ == "__main__":
    main()