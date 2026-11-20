#!/usr/bin/env python3
"""Mixa voz + música + efeitos a partir de um plano JSON e gera um WAV 48 kHz estéreo.

Uso: python3 mixar.py <plano.json> <saida.wav>

plano.json:
{
  "voz": {"arquivo": "...wav", "lufs_alvo": -16},
  "duracao": 49.04,
  "musica_abaixo_da_voz_lu": 16,        # nível da música (antes do ducking), em LU abaixo da voz
  "ducking": {"limiar": 0.04, "razao": 4, "ataque_ms": 60, "soltura_ms": 500},
  "musicas": [ {"id": "mus01", "arquivo": "...mp3", "origem_ini": 0.0, "destino_ini": 0.0,
                "duracao": 37.0, "fade_in": 0.6, "fade_out": 1.2, "ajuste_db": 0} ],
  "sfx": [ {"id": "sfx01", "arquivo": "...", "origem_ini": 0.0, "destino_ini": 3.2, "duracao": 0.8,
            "abaixo_da_voz_lu": 14, "ajuste_db": 0, "fade_out": 0.05} ]
}

Regras (perfil estilo-som.md): a voz sempre clara; a música abaixa sob a voz (sidechain) e sobe
um pouco nos respiros; efeitos bem abaixo da voz; fades em tudo (sem estalo); teto de pico -1 dBTP.
O nível de cada trecho é medido (LUFS) no próprio trecho usado, não no arquivo inteiro.
"""
import json
import re
import subprocess
import sys


def lufs(arquivo, ini=None, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if ini is not None:
        cmd += ["-ss", str(ini)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", arquivo, "-af", "ebur128", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    v = float(m[-1]) if m else -70.0
    return v if v > -69 else -40.0  # trecho quase mudo: evita ganho absurdo


def rms_db(arquivo, ini=0.0, dur=None):
    """Nível RMS (dBFS) do trecho: para sons curtos (< 0,4 s) o LUFS integrado não mede."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-ss", str(ini)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", arquivo, "-af", "astats=measure_overall=RMS_level:measure_perchannel=none", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.findall(r"RMS level dB:\s+(-?[\d.]+)", out)
    return float(m[-1]) if m else -30.0


def main():
    plano = json.load(open(sys.argv[1], encoding="utf-8"))
    saida = sys.argv[2]
    voz = plano["voz"]
    alvo_voz = voz.get("lufs_alvo", -16)
    g_voz = alvo_voz - lufs(voz["arquivo"])
    dur = plano["duracao"]
    ins, filtros, n = ["-i", voz["arquivo"]], [], 1
    filtros.append(f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g_voz:.2f}dB,apad,atrim=0:{dur}[voz]")

    mus_labels = []
    for m in plano.get("musicas", []):
        alvo = alvo_voz - plano.get("musica_abaixo_da_voz_lu", 16) + m.get("ajuste_db", 0)
        g = alvo - lufs(m["arquivo"], m["origem_ini"], m["duracao"])
        ins += ["-ss", str(m["origem_ini"]), "-t", str(m["duracao"]), "-i", m["arquivo"]]
        fo_ini = max(0, m["duracao"] - m.get("fade_out", 1.0))
        d_ms = int(round(m["destino_ini"] * 1000))
        filtros.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g:.2f}dB,"
                       f"afade=t=in:d={m.get('fade_in', 0.5)},afade=t=out:st={fo_ini:.3f}:d={m.get('fade_out', 1.0)},"
                       f"adelay={d_ms}|{d_ms}[{m['id']}]")
        mus_labels.append(f"[{m['id']}]"); n += 1

    if mus_labels:
        dk = plano.get("ducking", {})
        filtros.append(f"{''.join(mus_labels)}amix=inputs={len(mus_labels)}:normalize=0,apad,atrim=0:{dur}[musbus]")
        filtros.append("[voz]asplit=2[voz1][vozsc]")
        filtros.append(f"[musbus][vozsc]sidechaincompress=threshold={dk.get('limiar', 0.04)}:ratio={dk.get('razao', 4)}:"
                       f"attack={dk.get('ataque_ms', 60)}:release={dk.get('soltura_ms', 500)}:makeup=1[musduck]")
        bus = ["[voz1]", "[musduck]"]
    else:
        bus = ["[voz]"]

    for s in plano.get("sfx", []):
        alvo = alvo_voz - s.get("abaixo_da_voz_lu", 14) + s.get("ajuste_db", 0)
        g = alvo - rms_db(s["arquivo"], s.get("origem_ini", 0), s["duracao"])  # RMS ≈ LUFS para estes sons
        ins += ["-ss", str(s.get("origem_ini", 0)), "-t", str(s["duracao"]), "-i", s["arquivo"]]
        fo = s.get("fade_out", 0.05)
        d_ms = int(round(s["destino_ini"] * 1000))
        filtros.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g:.2f}dB,"
                       f"afade=t=in:d=0.01,afade=t=out:st={max(0, s['duracao'] - fo):.3f}:d={fo},adelay={d_ms}|{d_ms}[{s['id']}]")
        bus.append(f"[{s['id']}]"); n += 1

    filtros.append(f"{''.join(bus)}amix=inputs={len(bus)}:normalize=0,atrim=0:{dur},alimiter=limit=0.89:level=false[out]")
    cmd = ["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(filtros), "-map", "[out]",
                                                   "-ar", "48000", "-c:a", "pcm_s16le", saida]
    subprocess.run(cmd, check=True)
    print(f"mix: {saida} · voz {g_voz:+.1f} dB · {len(mus_labels)} músicas · {len(plano.get('sfx', []))} efeitos · "
          f"loudness final {lufs(saida):.1f} LUFS")


if __name__ == "__main__":
    main()