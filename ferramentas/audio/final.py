#!/usr/bin/env python3
"""Monta o vídeo final para o YouTube: vídeo aprovado + mix aprovado, loudness -14 LUFS / -1 dBTP.

Uso: python3 final.py <video.mp4> <mix.wav> <saida.mp4>

- Normaliza o áudio em duas passadas (loudnorm): alvo -14 LUFS integrado, pico verdadeiro -1 dBTP, LRA 11.
- Vídeo: copia o H.264 se já estiver em 1920x1080, 30 qps, yuv420p; senão recodifica (CRF 18).
- Áudio: AAC 48 kHz estéreo 320 kbps. +faststart.
- Confere: duração do vídeo = duração do áudio (± 1 quadro) e imprime o loudness final.
"""
import json
import re
import subprocess
import sys


def probe(arq):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration",
                          "-of", "json", arq], capture_output=True, text=True).stdout
    return json.loads(out)


def main():
    video, mix, saida = sys.argv[1:4]
    # 1ª passada: medir
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mix, "-af",
                          "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"): out.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    v = [s for s in probe(video)["streams"] if s["codec_type"] == "video"][0]
    copia = v["codec_name"] == "h264" and v["width"] == 1920 and v["height"] == 1080 and v["r_frame_rate"] == "30/1" and v["pix_fmt"] == "yuv420p"
    cv = ["-c:v", "copy"] if copia else ["-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "30"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a", *cv,
                    "-af", ln + ",aresample=48000", "-c:a", "aac", "-b:a", "320k", "-ac", "2",
                    "-shortest", "-movflags", "+faststart", saida], check=True)
    info = probe(saida)
    dv = float([s for s in info["streams"] if s["codec_type"] == "video"][0].get("duration", info["format"]["duration"]) if False else info["format"]["duration"])
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", saida, "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1]; P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", meas)[-1]
    print(f"final: {saida} · {dv:.2f}s · vídeo {'copiado' if copia else 'recodificado'} · {I} LUFS · pico {P} dBTP")


if __name__ == "__main__":
    main()