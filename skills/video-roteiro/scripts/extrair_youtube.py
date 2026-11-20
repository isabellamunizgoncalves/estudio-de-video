#!/usr/bin/env python3
"""Extrai metadados, comentarios e transcricao de um video do YouTube.

Uso:
    python extrair_youtube.py "<URL>" [--out analise] [--max-comentarios 300]

Saida:
    <out>/<video_id>/contexto.md   -> resumo legivel para analise emocional
    <out>/<video_id>/contexto.json -> dados brutos (comentarios completos)

Requisito: yt-dlp (pip install yt-dlp).
Opcional: youtube-transcript-api (pip install youtube-transcript-api) para transcricao.

Codigos de saida:
    0 = sucesso
    2 = yt-dlp nao encontrado
    3 = falha na extracao
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def extract_video_id(url: str) -> str:
    padroes = [
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"(?:v=|/v/|embed/|live/|shorts/)([0-9A-Za-z_-]{11})",
    ]
    for padrao in padroes:
        encontrado = re.search(padrao, url)
        if encontrado:
            return encontrado.group(1)
    return "video"


def candidatos_yt_dlp() -> list[list[str]]:
    candidatos: list[list[str]] = []
    executavel = shutil.which("yt-dlp")
    if executavel:
        candidatos.append([executavel])
    for python in (sys.executable, "python", "py"):
        if python and python not in [c[0] for c in candidatos]:
            candidatos.append([python, "-m", "yt_dlp"])
    return candidatos


def extrair_com_yt_dlp(url: str) -> tuple[dict | None, str]:
    base = [
        "--write-comments",
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
        "--no-warnings",
        "--no-progress",
        "--no-cache-dir",
        "--socket-timeout", "15",
        "--retries", "1",
        "--extractor-retries", "1",
    ]
    erros: list[str] = []
    for candidato in candidatos_yt_dlp():
        try:
            resultado = subprocess.run(
                candidato + base + [url],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired:
            erros.append(f"{' '.join(candidato)}: tempo limite atingido")
            break
        except (OSError, subprocess.SubprocessError) as exc:
            erros.append(f"{' '.join(candidato)}: {exc}")
            continue
        if resultado.returncode == 0 and resultado.stdout.strip():
            try:
                return json.loads(resultado.stdout), ""
            except json.JSONDecodeError as exc:
                erros.append(f"{' '.join(candidato)}: JSON invalido ({exc})")
                continue
        detalhe = (resultado.stderr or resultado.stdout or "").strip().splitlines()
        erros.append(f"{' '.join(candidato)}: {detalhe[-1] if detalhe else 'sem detalhes'}")
    return None, " | ".join(erros[-3:])


def texto_comentario(comentario: dict) -> str:
    texto = comentario.get("text") or comentario.get("content") or ""
    if isinstance(texto, list):
        partes = []
        for parte in texto:
            if isinstance(parte, dict):
                partes.append(parte.get("string") or parte.get("text") or "")
            else:
                partes.append(str(parte))
        return "".join(partes).strip()
    return str(texto).strip()


def buscar_transcricao(video_id: str) -> tuple[list | None, str]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return None, "youtube-transcript-api nao instalado (opcional)"
    try:
        try:
            api = YouTubeTranscriptApi()
            legenda = api.fetch(video_id, languages=["pt", "pt-BR", "fr", "en"])
            dados = legenda.to_raw_data() if hasattr(legenda, "to_raw_data") else legenda
        except (TypeError, AttributeError):
            dados = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["pt", "pt-BR", "fr", "en"]
            )
        return list(dados), ""
    except Exception as exc:  # a API tem varios tipos de erro especificos
        return None, str(exc)


def formatar_timestamp(segundos: float | int | None) -> str:
    if segundos is None:
        return "--:--"
    total = int(segundos)
    return f"{total // 60:02d}:{total % 60:02d}"


def montar_markdown(info: dict, comentarios: list[dict], transcricao: list | None,
                    aviso_transcricao: str, max_comentarios: int, url: str) -> str:
    titulo = info.get("title") or "(sem titulo)"
    canal = info.get("channel") or info.get("uploader") or "(desconhecido)"
    duracao = info.get("duration") or 0
    visualizacoes = info.get("view_count") or 0
    curtidas = info.get("like_count") or 0
    total_comentarios = info.get("comment_count") or info.get("n_comments") or len(comentarios)

    linhas: list[str] = []
    linhas.append(f"# Contexto extraido: {titulo}")
    linhas.append("")
    linhas.append(f"- **URL:** {url}")
    linhas.append(f"- **ID:** {info.get('id') or extract_video_id(url)}")
    linhas.append(f"- **Canal:** {canal}")
    linhas.append(f"- **Duracao:** {formatar_timestamp(duracao)}")
    linhas.append(f"- **Visualizacoes:** {visualizacoes:,}".replace(",", "."))
    linhas.append(f"- **Curtidas:** {curtidas:,}".replace(",", "."))
    linhas.append(f"- **Comentarios no video:** {total_comentarios:,}".replace(",", "."))
    linhas.append(f"- **Comentarios nesta amostra:** {len(comentarios)}")
    linhas.append(f"- **Extraido em:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    linhas.append("")

    descricao = str(info.get("description") or "").strip()
    if descricao:
        linhas.append("## Descricao")
        linhas.append("")
        linhas.append(descricao[:4000])
        linhas.append("")

    linhas.append("## Comentarios (ordenados por curtidas)")
    linhas.append("")
    if not comentarios:
        linhas.append("Nenhum comentario extraido. Usar o fallback manual descrito na SKILL.md.")
    else:
        for indice, comentario in enumerate(comentarios[:max_comentarios], start=1):
            texto = texto_comentario(comentario)
            if not texto:
                continue
            autor = comentario.get("author") or "anonimo"
            likes = comentario.get("like_count") or 0
            data = comentario.get("timestamp")
            data_txt = ""
            if isinstance(data, (int, float)):
                data_txt = datetime.fromtimestamp(data, timezone.utc).strftime("%Y-%m-%d")
            elif isinstance(data, str):
                data_txt = data[:10]
            texto = " ".join(texto.split())
            if len(texto) > 900:
                texto = texto[:900] + " [...]"
            linhas.append(f"**{indice}. {autor}** — {likes} curtidas" +
                          (f" — {data_txt}" if data_txt else ""))
            linhas.append(f"> {texto}")
            linhas.append("")
    linhas.append("## Transcricao")
    linhas.append("")
    if not transcricao:
        linhas.append(f"Nao disponivel. {aviso_transcricao}".strip())
    else:
        bloco: list[str] = []
        for parte in transcricao:
            if not isinstance(parte, dict):
                continue
            inicio = parte.get("start") or parte.get("offset") or 0
            try:
                inicio = float(str(inicio).rstrip("s"))
            except ValueError:
                inicio = 0
            texto = str(parte.get("text") or "").replace("\n", " ").strip()
            if texto:
                bloco.append(f"[{formatar_timestamp(inicio)}] {texto}")
        for i in range(0, len(bloco), 25):
            linhas.extend(bloco[i:i + 25])
            linhas.append("")
    return "\n".join(linhas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extrai contexto de um video do YouTube.")
    parser.add_argument("url", help="URL do video do YouTube")
    parser.add_argument("--out", default="analise", help="diretorio de saida (padrao: analise)")
    parser.add_argument("--max-comentarios", type=int, default=300,
                        help="quantidade maxima de comentarios no Markdown (padrao: 300)")
    parser.add_argument("--sem-transcricao", action="store_true",
                        help="nao tentar buscar a transcricao")
    args = parser.parse_args()

    if not candidatos_yt_dlp():
        print("ERRO: yt-dlp nao encontrado. Instale com: pip install yt-dlp", file=sys.stderr)
        return 2

    print("Extraindo metadados e comentarios...")
    info, erro = extrair_com_yt_dlp(args.url)
    if info is None:
        print(f"ERRO na extracao: {erro}", file=sys.stderr)
        print("Fallback: peca ao usuario que cole os comentarios.", file=sys.stderr)
        return 3

    comentarios = list(info.get("comments") or info.get("comment_entries") or [])
    for comentario in comentarios:
        if not isinstance(comentario, dict):
            continue
        try:
            comentario["like_count"] = int(comentario.get("like_count") or 0)
        except (TypeError, ValueError):
            comentario["like_count"] = 0
    comentarios.sort(key=lambda c: c.get("like_count", 0), reverse=True)

    aviso_transcricao = ""
    transcricao = None
    if not args.sem_transcricao:
        print("Tentando buscar transcricao...")
        transcricao, aviso_transcricao = buscar_transcricao(
            str(info.get("id") or extract_video_id(args.url))
        )

    video_id = str(info.get("id") or extract_video_id(args.url))
    destino = Path(args.out) / video_id
    destino.mkdir(parents=True, exist_ok=True)

    markdown = montar_markdown(
        info, comentarios, transcricao, aviso_transcricao,
        args.max_comentarios, args.url
    )
    caminho_md = destino / "contexto.md"
    caminho_json = destino / "contexto.json"
    caminho_md.write_text(markdown, encoding="utf-8")
    caminho_json.write_text(
        json.dumps({"info": info, "comments": comentarios, "transcript": transcricao},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK: {len(comentarios)} comentarios extraidos.")
    print(f"Transcricao: {'disponivel' if transcricao else 'indisponivel'}")
    print(f"Markdown: {caminho_md}")
    print(f"JSON: {caminho_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
