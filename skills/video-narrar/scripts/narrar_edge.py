"""Narra um roteiro com Edge TTS (vozes neurais da Microsoft), parágrafo por parágrafo, com pausas.

Uso (da raiz do repo):
  .venv-edicao/bin/python skills/video-narrar/scripts/narrar_edge.py --projeto projects/retrovisage-04
  .venv-edicao/bin/python skills/video-narrar/scripts/narrar_edge.py texto.txt --saida teste.wav --voz fr-FR-HenriNeural

Com --projeto: lê Roteiro/roteiro_humanizado.txt (senão Roteiro/roteiro.txt) e grava
Narracao/narracao_vNN.wav numa versão nova (nunca sobrescreve) + a ficha narracao_vNN.json.

Linha em branco no texto = pausa; parágrafo curto isolado (frase de impacto) ganha pausa maior.
Requer: pip install edge-tts · ffmpeg no sistema · internet (o texto é enviado à Microsoft).
"""
import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("❌ Falta o pacote edge-tts: .venv-edicao/bin/pip install edge-tts")

SR = 24000  # taxa nativa do Edge TTS


def args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("texto", type=Path, nargs="?", help="Arquivo de texto (padrão com --projeto: Roteiro/roteiro_humanizado.txt)")
    p.add_argument("--projeto", type=Path, help="Pasta do vídeo (projects/<slug>): lê de Roteiro/, grava em Narracao/")
    p.add_argument("--saida", type=Path, help="Arquivo .wav de saída (padrão: Narracao/narracao_vNN.wav)")
    p.add_argument("--voz", default="fr-FR-RemyMultilingualNeural", help="Voz do Edge (padrão: Remy)")
    p.add_argument("--rate", default="-8%", help="Velocidade, ex.: -8%% (mais lento), +5%% (padrão: -8%%)")
    p.add_argument("--pausa", type=float, default=0.75, help="Silêncio entre parágrafos, em segundos (padrão 0,75)")
    p.add_argument("--pausa-curta", type=float, default=1.1, help="Silêncio depois de frase curta isolada (padrão 1,1)")
    p.add_argument("--paralelo", type=int, default=4, help="Parágrafos gerados ao mesmo tempo (padrão 4)")
    return p.parse_args()


def texto_padrao(projeto: Path) -> Path:
    for nome in ("roteiro_humanizado.txt", "roteiro.txt"):
        f = projeto / "Roteiro" / nome
        if f.exists():
            return f
    sys.exit(f"❌ Nenhum Roteiro/roteiro_humanizado.txt nem Roteiro/roteiro.txt em {projeto}")


def proxima_versao(pasta: Path) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    nums = [int(f.stem.split("_v")[-1]) for f in pasta.glob("narracao_v*.wav") if f.stem.split("_v")[-1].isdigit()]
    return pasta / f"narracao_v{max(nums, default=0) + 1:02d}.wav"


async def gerar_todos(blocos, voz, rate, tmp, paralelo):
    sem = asyncio.Semaphore(paralelo)

    async def um(i, texto):
        async with sem:
            for tentativa in range(4):
                try:
                    await edge_tts.Communicate(texto, voz, rate=rate).save(str(tmp / f"{i:04d}.mp3"))
                    return
                except Exception:
                    if tentativa == 3:
                        raise
                    await asyncio.sleep(2 * (tentativa + 1))

    await asyncio.gather(*(um(i, t) for i, t in enumerate(blocos)))


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def main():
    a = args()
    if a.texto is None:
        if not a.projeto:
            sys.exit("❌ Informe o arquivo de texto ou --projeto projects/<slug>")
        a.texto = texto_padrao(a.projeto)
    saida = a.saida or proxima_versao((a.projeto or a.texto.parent) / "Narracao")

    blocos = [b.strip().replace("\n", " ") for b in a.texto.read_text(encoding="utf-8").split("\n\n") if b.strip()]
    print(f"📄 {a.texto} — {len(blocos)} parágrafos · voz {a.voz} · rate {a.rate}")

    tmp = Path(tempfile.mkdtemp(prefix="narracao_edge_"))
    try:
        t0 = time.time()
        asyncio.run(gerar_todos(blocos, a.voz, a.rate, tmp, a.paralelo))

        silencios = {}
        def silencio(seg):
            if seg not in silencios:
                f = tmp / f"sil_{seg}.wav"
                ff("-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(seg), str(f))
                silencios[seg] = f
            return silencios[seg]

        lista = tmp / "lista.txt"
        with lista.open("w") as L:
            for i, t in enumerate(blocos):
                w = tmp / f"{i:04d}.wav"
                ff("-i", str(tmp / f"{i:04d}.mp3"), "-ar", str(SR), "-ac", "1", str(w))
                L.write(f"file '{w}'\n")
                if i < len(blocos) - 1:
                    curto = len(t.split()) <= 6
                    L.write(f"file '{silencio(a.pausa_curta if curto else a.pausa)}'\n")

        saida.parent.mkdir(parents=True, exist_ok=True)
        ff("-f", "concat", "-safe", "0", "-i", str(lista), "-c:a", "pcm_s16le", "-ar", str(SR), "-ac", "1", str(saida))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(saida)],
                               capture_output=True, text=True).stdout or 0)
    saida.with_suffix(".json").write_text(json.dumps({
        "arquivo": saida.name,
        "texto": str(a.texto),
        "motor": "edge-tts",
        "voz": a.voz,
        "rate": a.rate,
        "pausa": a.pausa,
        "pausa_curta": a.pausa_curta,
        "duracao_s": round(dur, 1),
        "criado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ {saida} — {int(dur // 60)} min {int(dur % 60):02d} s, gerado em {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
