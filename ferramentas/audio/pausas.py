#!/usr/bin/env python3
"""Encurta as pausas longas demais da narração e gera uma versão nova, com a tabela de tempos.

Uso: python3 pausas.py <pasta-do-video> <audio-original> <versao> [--frase 0.40] [--paragrafo 0.90] [--min 0.20] [--folga 0.15]

Lê   _CLAUDE/transcricao/roteiro_tempos.json
Gera _CLAUDE/narracao/narracao_vNN.wav            (48 kHz, mesmo número de canais)
     _CLAUDE/narracao/mapa_tempo_vNN.json          trechos mantidos: [{"orig_ini", "orig_fim", "novo_ini"}]
     _CLAUDE/transcricao/roteiro_tempos_vNN.json   tempos das palavras já na narração nova
     _CLAUDE/transcricao/frases.md                 reescrito no tempo novo

Regras (perfil estilo-cortes.md): pausa entre frases até --frase s; entre parágrafos até --paragrafo s.
Pausa dentro da frase não é mexida. Nunca corta dentro de palavra: o corte cai no meio do silêncio.
Fades de 10 ms em cada emenda (sem estalo).
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
from conferir_roteiro import escrever_frases  # noqa: E402


def arg(nome, padrao):
    return float(sys.argv[sys.argv.index(nome) + 1]) if nome in sys.argv else padrao


def main():
    pasta, audio, versao = sys.argv[1], sys.argv[2], int(sys.argv[3])
    lim_frase, lim_par, minimo = arg("--frase", 0.40), arg("--paragrafo", 0.90), arg("--min", 0.20)
    folga = arg("--folga", 0.15)
    d = os.path.join(pasta, "_CLAUDE")
    with open(os.path.join(d, "transcricao", "roteiro_tempos.json"), encoding="utf-8") as f:
        pal = json.load(f)

    tmp = os.path.join(d, "tmp"); os.makedirs(tmp, exist_ok=True)
    wav48 = os.path.join(tmp, "orig48k.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ar", "48000", wav48], check=True)
    dados, sr = sf.read(wav48, always_2d=True)
    dur = len(dados) / sr

    # Pedidos de Isabella: --alongar "42.2=0.5,10.3=0.8" (pausa depois da palavra que termina em ~42.2 s passa a 0.5 s).
    pedidos = {}
    if "--alongar" in sys.argv:
        for par in sys.argv[sys.argv.index("--alongar") + 1].split(","):
            t, v = par.split("=")
            pedidos[float(t)] = float(v)

    # Edições: (inicio, fim, inserir). Corte: remove [inicio, fim]. Inserção: inicio == fim, insere silêncio.
    cortes, mudancas = [], []
    for i in range(len(pal) - 1):
        a, b = pal[i], pal[i + 1]
        if a.get("sem_tempo") or b.get("sem_tempo"):
            continue
        gap = b["ini"] - a["fim"]
        pedido = next((v for t, v in pedidos.items() if abs(t - a["fim"]) <= 0.1), None)
        if pedido is not None:
            meio = a["fim"] + gap / 2
            if pedido > gap:
                cortes.append((meio, meio, pedido - gap))
            else:
                cortes.append((meio - (gap - pedido) / 2, meio + (gap - pedido) / 2, 0.0))
            mudancas.append({"tempo": round(a["fim"], 2), "de": round(gap, 2), "para": pedido, "tipo": "pedido"})
            continue
        if b["frase"] == a["frase"]:
            continue
        alvo = lim_par if b["par"] != a["par"] else lim_frase
        if gap > alvo + folga:  # só vale cortar se sobra bastante (cortes de centésimos não se ouvem)
            sobra = gap - alvo
            meio = a["fim"] + gap / 2
            cortes.append((meio - sobra / 2, meio + sobra / 2, 0.0))
            mudancas.append({"tempo": round(a["fim"], 2), "de": round(gap, 2), "para": alvo,
                             "tipo": "paragrafo" if b["par"] != a["par"] else "frase"})
        elif gap < minimo:
            mudancas.append({"tempo": round(a["fim"], 2), "de": round(gap, 2), "para": None,
                             "tipo": "curta demais (não alterada: avisar)"})

    # Trechos mantidos, cada um com o silêncio a inserir depois dele.
    cortes.sort()
    mantidos, t = [], 0.0
    for c0, c1, ins in cortes:
        mantidos.append((t, c0, ins)); t = c1
    mantidos.append((t, dur, 0.0))

    fade = int(0.010 * sr)
    pedacos, mapa, novo = [], [], 0.0
    for k, (a, b, ins) in enumerate(mantidos):
        x = dados[int(a * sr): int(b * sr)].copy()
        if k > 0 and len(x) > fade:
            x[:fade] *= np.linspace(0, 1, fade)[:, None]
        if k < len(mantidos) - 1 and len(x) > fade:
            x[-fade:] *= np.linspace(1, 0, fade)[:, None]
        pedacos.append(x)
        mapa.append({"orig_ini": round(a, 4), "orig_fim": round(b, 4), "novo_ini": round(novo, 4)})
        novo += len(x) / sr
        if ins > 0:
            pedacos.append(np.zeros((int(round(ins * sr)), dados.shape[1])))
            novo += int(round(ins * sr)) / sr
    saida = np.concatenate(pedacos)

    os.makedirs(os.path.join(d, "narracao"), exist_ok=True)
    nome = os.path.join(d, "narracao", f"narracao_v{versao:02d}.wav")
    sf.write(nome, saida, sr, subtype="PCM_16")
    with open(os.path.join(d, "narracao", f"mapa_tempo_v{versao:02d}.json"), "w") as f:
        json.dump({"cortes": mapa, "mudancas": mudancas}, f, ensure_ascii=False, indent=1)

    def conv(s):
        for m in mapa:
            if m["orig_ini"] - 1e-6 <= s <= m["orig_fim"] + 1e-6:
                return round(m["novo_ini"] + (s - m["orig_ini"]), 3)
        # caiu num corte: vai para o começo do trecho seguinte
        prox = next((m for m in mapa if m["orig_ini"] > s), mapa[-1])
        return round(prox["novo_ini"], 3)

    novos = [dict(p, ini=conv(p["ini"]), fim=conv(p["fim"])) for p in pal]
    with open(os.path.join(d, "transcricao", f"roteiro_tempos_v{versao:02d}.json"), "w", encoding="utf-8") as f:
        json.dump(novos, f, ensure_ascii=False, indent=0)
    escrever_frases(novos, os.path.join(d, "transcricao", "frases.md"))
    print(f"{dur:.2f}s -> {len(saida) / sr:.2f}s · {len(cortes)} pausas alteradas")
    for m in mudancas:
        print(f"  {m['tempo']:.2f}s {m['tipo']}: {m['de']}s -> {m['para']}")


if __name__ == "__main__":
    main()