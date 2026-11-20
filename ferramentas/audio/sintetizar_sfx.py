#!/usr/bin/env python3
"""Cria a biblioteca básica de efeitos sonoros por síntese (sem licença de terceiros, sem crédito).

Uso: .venv-edicao/bin/python -I sintetizar_sfx.py <pasta-de-saida>

Sons discretos, no estilo do perfil (papel, fita, arquivo, frio). Semente fixa: sai igual toda vez.
Cada som: WAV 48 kHz estéreo, com o silêncio do começo já removido (o ataque está no tempo 0,
exceto os que têm 'pico' indicado no índice, como o whoosh).
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

SR = 48000
rng = np.random.default_rng(1962)


def t(d):
    return np.arange(int(d * SR)) / SR


def ruido(d, cor="branco"):
    n = rng.standard_normal(int(d * SR))
    if cor == "rosa":  # 1/f aproximado (filtro de Paul Kellet simplificado)
        b = np.zeros(3); out = np.empty_like(n)
        for i, w in enumerate(n):
            b[0] = 0.99765 * b[0] + w * 0.0990460
            b[1] = 0.96300 * b[1] + w * 0.2965164
            b[2] = 0.57000 * b[2] + w * 1.0526913
            out[i] = b.sum() + w * 0.1848
        n = out / 4
    return n


def passa_baixa(x, fc):
    a = np.exp(-2 * np.pi * np.atleast_1d(fc) / SR)
    a = np.broadcast_to(a, x.shape) if a.size > 1 else np.full(x.shape, a[0])
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc; y[i] = acc
    return y


def passa_alta(x, fc):
    return x - passa_baixa(x, fc)


def faixa(x, f1, f2):
    return passa_baixa(passa_alta(x, f1), f2)


def env_exp(d, tau, ataque=0.002):
    tt = t(d); e = np.exp(-tt / tau)
    na = max(1, int(ataque * SR)); e[:na] *= np.linspace(0, 1, na)
    return e


def norm(x, pico=0.9):
    m = np.max(np.abs(x)) or 1.0
    return x / m * pico


def estereo(x, largura=0.15):
    atraso = int(0.0007 * SR)
    l = x; r = np.concatenate([np.zeros(atraso), x[:-atraso]]) if largura else x
    return np.stack([l * (1 - largura / 2) + r * largura / 2, r * (1 - largura / 2) + l * largura / 2], axis=1)


def batida_suave(d=0.35):          # laranja pousando na mesa
    tt = t(d); f = 95 * np.exp(-tt * 6) + 55
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, 0.07)
    toque = passa_baixa(ruido(d), 1800) * env_exp(d, 0.012)
    return norm(corpo + 0.6 * toque)


def papel_rasga(d=0.7):            # rasgo de papel: grãos crepitantes numa faixa que sobe
    n = ruido(d); tt = t(d)
    graos = (rng.random(len(n)) < (0.02 + 0.06 * tt / d)).astype(float)
    graos = passa_baixa(graos, 900) * 8
    corpo = faixa(n, 900 + 2500 * tt / d, 6500) * (0.4 + graos)
    e = np.minimum(1, tt / 0.05) * np.minimum(1, (d - tt) / 0.12)
    return norm(corpo * e)


def fita_cola(d=0.22):             # fita adesiva colando: estalo curto + chiado grudento
    n = ruido(d)
    estalo = passa_alta(n, 1500) * env_exp(d, 0.006)
    gruda = faixa(n, 2000, 7000) * env_exp(d, 0.06) * (0.5 + 0.5 * np.sin(2 * np.pi * 37 * t(d)))
    return norm(estalo + 0.35 * gruda)


def fita_bate(d=0.4):              # fita grande batendo: tapa de papel + grave
    return norm(0.8 * fita_cola(d) + batida_suave(d) * 0.9)


def whoosh(d=0.9, pico=0.62):      # passagem de ar; pico de intensidade em 'pico' (fração)
    n = ruido(d, "rosa"); tt = t(d) / d
    env = np.exp(-((tt - pico) ** 2) / (2 * 0.16 ** 2))
    fc = 500 + 2600 * env
    return norm(passa_baixa(passa_alta(n, 150), fc) * env)


def tilintar(d=1.0, n=7):          # sininhos das luzes acendendo
    x = np.zeros(int(d * SR)); notas = [1568, 1760, 2093, 1976, 2349, 2093, 2637]
    for i in range(n):
        ini = int(i * 0.075 * SR); dd = d - i * 0.075
        tt = t(dd); f = notas[i % len(notas)]
        s = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt)) * env_exp(dd, 0.18)
        x[ini:ini + len(s)] += s[: len(x) - ini]
    return norm(x, 0.8)


def tv_chiado(d=0.7):              # televisor ligando: clique + chiado com zumbido
    tt = t(d); n = ruido(d)
    clique = passa_alta(n, 3000) * env_exp(d, 0.004)
    chiado = passa_alta(n, 2500) * 0.35 * (0.6 + 0.4 * (np.sin(2 * np.pi * 9 * tt) > 0))
    zumbido = 0.25 * np.sin(2 * np.pi * 50 * tt) + 0.1 * np.sin(2 * np.pi * 15734 / 100 * tt)
    e = np.minimum(1, (d - tt) / 0.2)
    return norm((clique + chiado + zumbido) * e)


def vento_gelado(d=3.5):           # vento frio que cresce e passa
    n = ruido(d, "rosa"); tt = t(d)
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.35 * tt + 1.0)
    fc = 300 + 900 * lfo
    e = np.minimum(1, tt / 0.8) * np.minimum(1, (d - tt) / 1.2)
    uivo = 0.15 * np.sin(2 * np.pi * (420 + 60 * lfo) * tt) * e
    return norm(passa_baixa(passa_alta(n, 120), fc) * lfo * e + uivo)


def carimbo(d=0.35):               # carimbo de borracha batendo no papel
    tt = t(d)
    madeira = np.sin(2 * np.pi * 190 * tt) * env_exp(d, 0.03) + 0.5 * np.sin(2 * np.pi * 870 * tt) * env_exp(d, 0.01)
    papel = passa_alta(ruido(d), 1200) * env_exp(d, 0.015)
    return norm(madeira + 0.5 * papel + 0.6 * batida_suave(d))


def folhear_jornal(d=1.25, n=3, passo=0.27):  # folhas de jornal caindo/folheando: passadas de papel com crepitar
    x = np.zeros(int(d * SR))
    for i in range(n):
        dd = 0.42; tt = t(dd); base = ruido(dd)
        graos = passa_baixa((rng.random(len(base)) < 0.05).astype(float), 1200) * 6
        env = np.sin(np.pi * np.minimum(1, tt / dd)) ** 2
        passada = faixa(base, 700 + 1800 * tt / dd, 5200) * env * (0.5 + graos)
        ini = int(i * passo * SR); fim = min(len(x), ini + len(passada))
        x[ini:fim] += passada[: fim - ini] * (1 - 0.15 * i)
    return norm(x)


def grave_apice(d=1.2):            # impacto grave do ápice
    tt = t(d); f = 70 * np.exp(-tt * 3) + 38
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, 0.35, 0.004))


SONS = {
    "batida/batida_suave_01": (batida_suave, {}),
    "papel/papel_rasga_01": (papel_rasga, {}),
    "fita/fita_cola_01": (fita_cola, {}),
    "fita/fita_bate_01": (fita_bate, {}),
    "whoosh/whoosh_suave_01": (whoosh, {"pico": 0.62}),
    "sino/tilintar_luzes_01": (tilintar, {}),
    "maquina/tv_liga_01": (tv_chiado, {}),
    "ambiente/vento_gelado_01": (vento_gelado, {}),
    "impacto/carimbo_01": (carimbo, {}),
    "impacto/grave_apice_01": (grave_apice, {}),
    "papel/folhear_jornal_01": (folhear_jornal, {}),
}


def main():
    raiz = sys.argv[1]; indice = {}
    for nome, (f, kw) in SONS.items():
        x = f(**kw)
        caminho = os.path.join(raiz, nome + ".wav"); os.makedirs(os.path.dirname(caminho), exist_ok=True)
        sf.write(caminho, estereo(x), SR, subtype="PCM_16")
        e = np.abs(x); pico = float(np.argmax(passa_baixa(e, 30)) / SR)
        indice[nome] = {"duracao": round(len(x) / SR, 3), "tempo_ate_pico": round(pico, 3), "origem": "síntese própria (sem licença de terceiros)"}
        print(f"{nome}: {len(x) / SR:.2f}s, pico em {pico:.2f}s")
    json.dump(indice, open(os.path.join(raiz, "indice.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()