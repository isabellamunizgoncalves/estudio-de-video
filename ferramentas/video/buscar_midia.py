#!/usr/bin/env python3
"""Busca fotos e vídeos de apoio para um vídeo, nos acervos com API oficial.

Lê um plano de busca (JSON) e, para cada item, baixa os melhores candidatos de
cada acervo, anotando fonte e licença. Não escolhe nada: quem escolhe é a
/video-imagens, olhando a folha de contato.

Uso:
    python ferramentas/video/buscar_midia.py \\
        --projeto projects/retrovisage-03 \\
        --plano projects/retrovisage-03/_CLAUDE/imagens/plano-busca.json

Formato do plano (lista de itens):
    [{"id": "vid01",
      "bloco": "Gancho",
      "descricao": "Uma mão abrindo um armário de cozinha",
      "tipo": "video",                      # video | foto
      "acervos": ["pixabay"],               # pixabay | commons
      "termos": ["opening kitchen cabinet", "main ouvrant placard"]}]

Saída:
    <projeto>/_CLAUDE/imagens/busca/candidatos/<id>/<acervo>_<n>.<ext>
    <projeto>/_CLAUDE/imagens/busca/candidatos.json   (fonte, licença, autor, link)

Acervos e chaves:
    Pixabay  — chave em PIXABAY_API_KEY (vai na URL; nunca imprimir a URL).
    Commons  — sem chave; baixa miniaturas de thumb.wikimedia.org com
               User-Agent identificado e pausa entre pedidos (o original em
               upload.wikimedia.org responde 429).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "EstudioDeVideo/1.0 (ferramenta de edicao; contato pelo repositorio)"
PAUSA = 1.2           # segundos entre pedidos ao mesmo acervo
TENTATIVAS = 3
LARGURA_MIN_VIDEO = 1280
LADO_MIN_FOTO = 800


# --------------------------------------------------------------------------- rede

def _pedir(url: str, *, binario: bool = False):
    """GET com User-Agent e repetição em erro temporário."""
    ultimo = None
    for tentativa in range(TENTATIVAS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                dados = r.read()
            return dados if binario else json.loads(dados.decode())
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(PAUSA * (tentativa + 2))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            ultimo = e
            time.sleep(PAUSA * (tentativa + 2))
    raise RuntimeError(f"falhou depois de {TENTATIVAS} tentativas: {ultimo}")


# ----------------------------------------------------------------------- pixabay

def _pixabay(termo: str, tipo: str, quantos: int) -> list[dict]:
    """Candidatos do Pixabay. Vídeo: versão HD (nunca 4K, pesa no render)."""
    base = "https://pixabay.com/api/videos/" if tipo == "video" else "https://pixabay.com/api/"
    params = {
        "key": os.environ.get("PIXABAY_API_KEY", "dummy"),
        "q": termo,
        "per_page": str(max(3, min(quantos * 3, 50))),
        "safesearch": "true",
    }
    if tipo == "foto":
        params["image_type"] = "photo"
    dados = _pedir(base + "?" + urllib.parse.urlencode(params))

    saida = []
    for hit in dados.get("hits", []):
        if tipo == "video":
            vs = hit.get("videos", {})
            # 'large' costuma ser 1920; 'medium' 1280. Evitar 4K.
            escolha = None
            for nome in ("large", "medium", "small"):
                v = vs.get(nome) or {}
                if v.get("url") and 0 < v.get("width", 0) <= 1920:
                    escolha = v
                    break
            if not escolha or escolha.get("width", 0) < LARGURA_MIN_VIDEO:
                continue
            saida.append({
                "url": escolha["url"], "largura": escolha.get("width"),
                "altura": escolha.get("height"), "ext": "mp4",
            })
        else:
            if min(hit.get("imageWidth", 0), hit.get("imageHeight", 0)) < LADO_MIN_FOTO:
                continue
            saida.append({
                "url": hit.get("largeImageURL"), "largura": hit.get("imageWidth"),
                "altura": hit.get("imageHeight"), "ext": "jpg",
            })
        saida[-1].update({
            "acervo": "pixabay", "autor": hit.get("user"),
            "pagina": hit.get("pageURL"),
            "licenca": "Pixabay Content License (uso comercial livre, crédito não obrigatório)",
        })
        if len(saida) >= quantos:
            break
    return saida


# ----------------------------------------------------------------------- commons

def _commons(termo: str, quantos: int) -> list[dict]:
    """Candidatos do Wikimedia Commons, como miniatura de até 1600 px."""
    busca = _pedir("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "list": "search", "srsearch": termo,
        "srnamespace": "6", "srlimit": str(quantos * 2), "format": "json",
    }))
    titulos = [h["title"] for h in busca.get("query", {}).get("search", [])]
    if not titulos:
        return []
    time.sleep(PAUSA)

    info = _pedir("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "titles": "|".join(titulos[:20]),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata",
        "iiurlwidth": "1600", "format": "json",
    }))

    saida = []
    for pag in info.get("query", {}).get("pages", {}).values():
        ii = (pag.get("imageinfo") or [{}])[0]
        if not ii.get("thumburl"):
            continue
        meta = ii.get("extmetadata", {})
        if min(ii.get("width", 0), ii.get("height", 0)) < LADO_MIN_FOTO:
            continue
        # a thumburl traz query string (?utm_...): a extensão sai só do caminho
        caminho = urllib.parse.urlparse(ii["thumburl"]).path
        saida.append({
            "url": ii["thumburl"], "ext": Path(caminho).suffix.lstrip(".").lower() or "jpg",
            "largura": ii.get("thumbwidth"), "altura": ii.get("thumbheight"),
            "acervo": "commons", "titulo": pag.get("title"),
            "autor": _texto(meta.get("Artist")), "pagina": ii.get("descriptionurl"),
            "licenca": _texto(meta.get("LicenseShortName")) or "ver página do arquivo",
        })
        if len(saida) >= quantos:
            break
    return saida


def _texto(campo) -> str:
    """extmetadata vem com HTML; tira as tags para caber no creditos.json."""
    import re
    if not campo:
        return ""
    return re.sub(r"<[^>]+>", "", str(campo.get("value", ""))).strip()


# -------------------------------------------------------------------- download

def _baixar(url: str, destino: Path) -> bool:
    try:
        destino.write_bytes(_pedir(url, binario=True))
        return destino.stat().st_size > 1024
    except Exception as e:
        print(f"    ! download falhou: {e}", file=sys.stderr)
        destino.unlink(missing_ok=True)
        return False


def _cortar(video: Path, segundos: float) -> None:
    """Corta o trecho útil e tira o áudio (o som é da /video-som)."""
    saida = video.with_name(video.stem + "_corte.mp4")
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-t", str(segundos), "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", str(saida)],
        capture_output=True, text=True)
    if r.returncode == 0 and saida.exists():
        video.unlink()
        saida.rename(video)
    else:
        print(f"    ! corte falhou em {video.name}: {r.stderr.strip()[:120]}", file=sys.stderr)


# ------------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True, type=Path)
    ap.add_argument("--plano", required=True, type=Path)
    ap.add_argument("--por-item", type=int, default=3, help="candidatos por item (padrão 3)")
    ap.add_argument("--duracao", type=float, default=5.0, help="segundos do corte de vídeo")
    ap.add_argument("--so", nargs="*", help="rodar só estes ids")
    args = ap.parse_args()

    plano = json.loads(args.plano.read_text(encoding="utf-8"))
    if args.so:
        plano = [i for i in plano if i["id"] in args.so]

    raiz = args.projeto / "_CLAUDE" / "imagens" / "busca"
    (raiz / "candidatos").mkdir(parents=True, exist_ok=True)
    registro: dict[str, list[dict]] = {}

    for item in plano:
        idn, tipo = item["id"], item.get("tipo", "foto")
        pasta = raiz / "candidatos" / idn
        pasta.mkdir(exist_ok=True)
        print(f"[{idn}] {tipo}: {item['descricao'][:60]}")

        achados: list[dict] = []
        for acervo in item.get("acervos", ["pixabay"]):
            for termo in item.get("termos", []):
                if len(achados) >= args.por_item:
                    break
                try:
                    novos = (_commons(termo, args.por_item - len(achados)) if acervo == "commons"
                             else _pixabay(termo, tipo, args.por_item - len(achados)))
                except Exception as e:
                    print(f"    ! {acervo} '{termo}': {e}", file=sys.stderr)
                    novos = []
                for n in novos:
                    n["termo"] = termo
                achados.extend(novos)
                time.sleep(PAUSA)

        guardados = []
        for n, cand in enumerate(achados[: args.por_item], 1):
            alvo = pasta / f"{cand['acervo']}_{n}.{cand['ext']}"
            if not _baixar(cand["url"], alvo):
                continue
            if tipo == "video":
                _cortar(alvo, args.duracao)
            cand["arquivo"] = str(alvo.relative_to(args.projeto))
            cand.pop("url", None)          # a URL direta do CDN expira; a página fica
            guardados.append(cand)
            print(f"    {n}. {cand['acervo']} — {cand.get('licenca','')[:48]}")

        if not guardados:
            print("    (nenhum candidato — refazer com outros termos)")
        registro[idn] = guardados

    (raiz / "candidatos.json").write_text(
        json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")

    total = sum(len(v) for v in registro.values())
    vazios = [k for k, v in registro.items() if not v]
    print(f"\n{total} candidatos em {len(registro)} itens → {raiz/'candidatos.json'}")
    if vazios:
        print(f"sem resultado: {', '.join(vazios)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
