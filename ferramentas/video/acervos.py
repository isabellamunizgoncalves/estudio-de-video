#!/usr/bin/env python3
"""Acervos com API oficial, um módulo por fonte, interface única.

Cada função de busca devolve uma lista de candidatos no mesmo formato:

    {"acervo", "url", "ext", "largura", "altura", "titulo", "autor",
     "pagina", "licenca", "tags", "remoto": bool}

`remoto=True` significa que o arquivo é grande demais para baixar inteiro
(filme de arquivo) e deve ser cortado direto da URL, por streaming.

Nenhuma raspagem de site e nenhum bloqueio de robô burlado: só API pública.
Gallica (BnF) responde 403 a acesso automatizado e por isso não está aqui.
Europeana, Pexels e Smithsonian exigem chave; entram quando houver uma.
"""

from __future__ import annotations

import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = "EstudioDeVideo/1.0 (ferramenta de edicao de video; contato pelo repositorio)"
PAUSA = 1.0
TENTATIVAS = 4
LARGURA_MIN_VIDEO = 1280
LADO_MIN_FOTO = 800


# --------------------------------------------------------------------- utilidades

def pedir(url: str, *, binario: bool = False, tentativas: int = TENTATIVAS):
    """GET com User-Agent e repetição em erro temporário (429/5xx)."""
    ultimo = None
    for n in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                dados = r.read()
            return dados if binario else json.loads(dados.decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(PAUSA * (n + 2))
                continue
            raise
        except Exception as e:                      # rede instável, JSON truncado
            ultimo = e
            time.sleep(PAUSA * (n + 2))
    raise RuntimeError(f"{tentativas} tentativas falharam: {ultimo}")


def _simples(txt: str) -> str:
    """Sem acento, minúsculo — para comparar termo com tags."""
    txt = unicodedata.normalize("NFKD", str(txt or ""))
    return "".join(c for c in txt if not unicodedata.combining(c)).lower()


def relevante(cand: dict, termo: str, contexto: list[str] | None = None) -> bool:
    """O candidato é o item pedido, ou só se parece com ele?

    Duas regras, aprendidas errando:

    1. **Palavra inteira, nunca pedaço.** `fish` casando com `fishing` trouxe
       barcos de pesca no lugar de um merlan frito.
    2. **Todas as palavras do termo, não qualquer uma.** `bouchée à la reine`
       exige `bouchee` e `reine`; só `reine` traz rainhas.

    `contexto` fecha o cerco em palavra ambígua entre idiomas: `souffle` é o
    prato e também o sopro, `mold` é a forma e o mofo (daí os morangos
    mofados da primeira rodada). Com contexto, pelo menos uma das palavras
    do domínio tem de aparecer também.
    """
    texto = _simples(" ".join(str(cand.get(c, "")) for c in ("tags", "titulo", "pagina")))
    tokens = set(re.split(r"\W+", texto))

    def tem(p: str) -> bool:
        return p in tokens or any(t.startswith(p) and len(t) - len(p) <= 2 for t in tokens)

    palavras = [p for p in re.split(r"\W+", _simples(termo)) if len(p) > 3]
    if palavras and not all(tem(p) for p in palavras):
        return False
    if contexto and not any(tem(_simples(c)) for c in contexto):
        return False
    return True


def _limpar_html(valor) -> str:
    if not valor:
        return ""
    v = valor.get("value", "") if isinstance(valor, dict) else valor
    return re.sub(r"<[^>]+>", "", str(v)).strip()


# ------------------------------------------------------------------------ pixabay

def pixabay(termo: str, tipo: str, quantos: int, contexto=None) -> list[dict]:
    """Vídeo e foto modernos. Chave na URL — nunca imprimir a URL montada."""
    base = "https://pixabay.com/api/videos/" if tipo == "video" else "https://pixabay.com/api/"
    p = {"key": os.environ.get("PIXABAY_API_KEY", "dummy"), "q": termo,
         "per_page": "40", "safesearch": "true"}
    if tipo == "foto":
        p["image_type"] = "photo"
    dados = pedir(base + "?" + urllib.parse.urlencode(p))

    saida = []
    for hit in dados.get("hits", []):
        base_cand = {"acervo": "pixabay", "tags": hit.get("tags", ""),
                     "autor": hit.get("user"), "pagina": hit.get("pageURL"),
                     "licenca": "Pixabay Content License (comercial livre, crédito não exigido)",
                     "remoto": False}
        if tipo == "video":
            escolha = next((v for n in ("large", "medium", "small")
                            for v in [hit.get("videos", {}).get(n) or {}]
                            if v.get("url") and LARGURA_MIN_VIDEO <= v.get("width", 0) <= 1920), None)
            if not escolha:
                continue
            base_cand.update(url=escolha["url"], ext="mp4",
                             largura=escolha.get("width"), altura=escolha.get("height"))
        else:
            if min(hit.get("imageWidth", 0), hit.get("imageHeight", 0)) < LADO_MIN_FOTO:
                continue
            base_cand.update(url=hit.get("largeImageURL"), ext="jpg",
                             largura=hit.get("imageWidth"), altura=hit.get("imageHeight"))
        if relevante(base_cand, termo, contexto):
            saida.append(base_cand)
        if len(saida) >= quantos:
            break
    return saida


# ------------------------------------------------------------------------ commons

def commons(termo: str, quantos: int, contexto=None) -> list[dict]:
    """Wikimedia Commons: fotos de época. Miniatura de até 1600 px — o
    original em upload.wikimedia.org responde 429."""
    busca = pedir("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "list": "search", "srsearch": termo, "srnamespace": "6",
        "srlimit": str(max(10, quantos * 3)), "format": "json"}))
    titulos = [h["title"] for h in busca.get("query", {}).get("search", [])]
    if not titulos:
        return []
    time.sleep(PAUSA)

    info = pedir("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "titles": "|".join(titulos[:25]), "prop": "imageinfo",
        "iiprop": "url|size|extmetadata", "iiurlwidth": "1600", "format": "json"}))

    saida = []
    for pag in info.get("query", {}).get("pages", {}).values():
        ii = (pag.get("imageinfo") or [{}])[0]
        if not ii.get("thumburl") or min(ii.get("width", 0), ii.get("height", 0)) < LADO_MIN_FOTO:
            continue
        meta = ii.get("extmetadata", {})
        caminho = urllib.parse.urlparse(ii["thumburl"]).path   # tira ?utm_...
        saida.append({
            "acervo": "commons", "url": ii["thumburl"],
            "ext": (caminho.rsplit(".", 1)[-1] or "jpg").lower(),
            "largura": ii.get("thumbwidth"), "altura": ii.get("thumbheight"),
            "titulo": pag.get("title"), "tags": pag.get("title", ""),
            "autor": _limpar_html(meta.get("Artist")),
            "pagina": ii.get("descriptionurl"),
            "licenca": _limpar_html(meta.get("LicenseShortName")) or "ver página do arquivo",
            "remoto": False})
        if not relevante(saida[-1], termo, contexto):
            saida.pop()
            continue
        if len(saida) >= quantos:
            break
    return saida


# --------------------------------------------------------------------- archive.org

def archive(termo: str, quantos: int, contexto=None, *, ano_ate: int | None = None) -> list[dict]:
    """Filmes de época em domínio público (Prelinger e afins).

    O arquivo não é baixado: é grande (centenas de MB) e só interessa um
    trecho. Marcado `remoto`, para ser cortado por streaming com ffmpeg.
    """
    q = f'({termo}) AND mediatype:(movies)'
    if ano_ate:
        q += f" AND year:[1900 TO {ano_ate}]"
    busca = pedir("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({
        "q": q, "fl[]": "identifier", "rows": str(max(6, quantos * 3)),
        "page": "1", "output": "json", "sort[]": "downloads desc"}))

    saida = []
    for doc in busca.get("response", {}).get("docs", []):
        ident = doc.get("identifier")
        if not ident:
            continue
        try:
            meta = pedir(f"https://archive.org/metadata/{ident}")
        except Exception:
            continue
        time.sleep(PAUSA)

        lic = (meta.get("metadata", {}) or {}).get("licenseurl", "")
        rights = (meta.get("metadata", {}) or {}).get("rights", "")
        titulo = (meta.get("metadata", {}) or {}).get("title", ident)

        arq = next((f for f in meta.get("files", [])
                    if f.get("name", "").lower().endswith((".mp4", ".m4v"))
                    and f.get("format", "").lower() not in ("thumbnail",)), None)
        if not arq:
            continue
        cand = {"acervo": "archive", "ext": "mp4", "remoto": True,
                "url": f"https://archive.org/download/{ident}/{urllib.parse.quote(arq['name'])}",
                "titulo": titulo, "tags": f"{titulo} {ident}",
                "autor": (meta.get("metadata", {}) or {}).get("creator", ""),
                "pagina": f"https://archive.org/details/{ident}",
                "licenca": lic or rights or "conferir na página do item",
                "largura": None, "altura": None}
        if relevante(cand, termo, contexto):
            saida.append(cand)
        if len(saida) >= quantos:
            break
    return saida


# ------------------------------------------------------- library of congress (LoC)

def loc(termo: str, quantos: int, contexto=None) -> list[dict]:
    """Fotos do acervo da Library of Congress; muitas "no known restrictions"."""
    dados = pedir("https://www.loc.gov/photos/?" + urllib.parse.urlencode({
        "q": termo, "fo": "json", "c": str(max(10, quantos * 3)), "at": "results"}))
    saida = []
    for r in (dados.get("results") or []):
        imgs = [u for u in (r.get("image_url") or []) if str(u).startswith("http")]
        if not imgs:
            continue
        url = imgs[-1]                                  # a última costuma ser a maior
        if url.startswith("//"):
            url = "https:" + url
        cand = {"acervo": "loc", "url": url, "ext": "jpg", "remoto": False,
                "titulo": r.get("title"), "tags": " ".join(
                    [str(r.get("title", ""))] + [str(s) for s in (r.get("subject") or [])]),
                "autor": "; ".join(r.get("contributor") or []) or "",
                "pagina": r.get("id") or r.get("url"),
                "licenca": (r.get("rights") or "ver página do item"),
                "largura": None, "altura": None}
        if relevante(cand, termo, contexto):
            saida.append(cand)
        if len(saida) >= quantos:
            break
    return saida


# ----------------------------------------------------------------------- openverse

def openverse(termo: str, quantos: int, contexto=None) -> list[dict]:
    """Agregador Creative Commons. Às vezes responde 504 no primeiro pedido;
    `pedir` repete."""
    dados = pedir("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
        "q": termo, "page_size": str(max(10, quantos * 3)),
        "license_type": "commercial,modification"}))
    saida = []
    for r in (dados.get("results") or []):
        url = r.get("url")
        if not url:
            continue
        if min(r.get("width") or 0, r.get("height") or 0) < LADO_MIN_FOTO:
            continue
        cand = {"acervo": "openverse", "url": url, "remoto": False,
                "ext": (urllib.parse.urlparse(url).path.rsplit(".", 1)[-1] or "jpg").lower()[:4],
                "largura": r.get("width"), "altura": r.get("height"),
                "titulo": r.get("title"), "tags": " ".join(
                    [str(r.get("title", ""))] + [t.get("name", "") for t in (r.get("tags") or [])]),
                "autor": r.get("creator") or "", "pagina": r.get("foreign_landing_url"),
                "licenca": f"{(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip()}
        if cand["ext"] not in ("jpg", "jpeg", "png", "webp"):
            cand["ext"] = "jpg"
        if relevante(cand, termo, contexto):
            saida.append(cand)
        if len(saida) >= quantos:
            break
    return saida


BUSCADORES = {
    "pixabay": pixabay, "commons": commons, "archive": archive,
    "loc": loc, "openverse": openverse,
}
