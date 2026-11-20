#!/usr/bin/env python3
"""Busca fotos e vídeos de apoio para um vídeo, nos acervos com API oficial.

Lê um plano de busca (JSON) e, para cada item, baixa os melhores candidatos,
anotando fonte e licença. Não escolhe nada: quem escolhe é a /video-imagens,
olhando a folha de contato.

Regra firme: **o item exato, não algo parecido.** Um candidato cujo título ou
tags não mencionem o termo é descartado. Item sem resultado fica vazio e é
listado no fim — folha com buraco declarado é melhor que folha preenchida com
o que não é.

Uso:
    python ferramentas/video/buscar_midia.py \\
        --projeto projects/retrovisage-03 \\
        --plano projects/retrovisage-03/_CLAUDE/imagens/plano-busca.json

Formato do plano (lista de itens):
    [{"id": "vid01",
      "bloco": "Gancho",
      "descricao": "Uma mão abrindo um armário de cozinha",
      "tipo": "video",                          # video | foto
      "acervos": ["pixabay", "archive"],        # pixabay commons archive loc openverse
      "termos": ["placard de cuisine", "kitchen cupboard"],
      "contexto": ["cuisine", "kitchen", "food"]}]   # fecha o cerco em palavra ambígua

Saída:
    <projeto>/_CLAUDE/imagens/busca/candidatos/<id>/<acervo>_<n>.<ext>
    <projeto>/_CLAUDE/imagens/busca/candidatos.json   (fonte, autor, licença, link)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import acervos  # noqa: E402


def _baixar(url: str, destino: Path) -> bool:
    try:
        destino.write_bytes(acervos.pedir(url, binario=True))
        return destino.stat().st_size > 2048
    except Exception as e:
        print(f"    ! download falhou: {str(e)[:90]}", file=sys.stderr)
        destino.unlink(missing_ok=True)
        return False


def _cortar_local(video: Path, segundos: float) -> None:
    """Corta o trecho útil e tira o áudio (o som é da /video-som)."""
    saida = video.with_name(video.stem + "_c.mp4")
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-t", str(segundos), "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", str(saida)], capture_output=True, text=True)
    if r.returncode == 0 and saida.exists():
        video.unlink()
        saida.rename(video)
    else:
        print(f"    ! corte falhou: {r.stderr.strip()[:110]}", file=sys.stderr)


def _cortar_remoto(url: str, destino: Path, segundos: float, inicio: float) -> bool:
    """Filme de arquivo: centenas de MB, e só interessa um trecho.

    O ffmpeg busca a posição direto na URL (o archive.org aceita pedidos por
    faixa), então nada é baixado inteiro.
    """
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(inicio), "-i", url,
         "-t", str(segundos), "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-vf", "scale='min(1920,iw)':-2", str(destino)],
        capture_output=True, text=True, timeout=420)
    if r.returncode == 0 and destino.exists() and destino.stat().st_size > 2048:
        return True
    print(f"    ! corte remoto falhou: {r.stderr.strip()[:110]}", file=sys.stderr)
    destino.unlink(missing_ok=True)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True, type=Path)
    ap.add_argument("--plano", required=True, type=Path)
    ap.add_argument("--por-item", type=int, default=3, help="candidatos por item (padrão 3)")
    ap.add_argument("--duracao", type=float, default=5.0, help="segundos do corte de vídeo")
    ap.add_argument("--inicio-arquivo", type=float, default=60.0,
                    help="de que segundo cortar o filme de arquivo (padrão 60: pula a abertura)")
    ap.add_argument("--so", nargs="*", help="rodar só estes ids")
    args = ap.parse_args()

    plano = json.loads(args.plano.read_text(encoding="utf-8"))
    if args.so:
        plano = [i for i in plano if i["id"] in args.so]

    raiz = args.projeto / "_CLAUDE" / "imagens" / "busca"
    (raiz / "candidatos").mkdir(parents=True, exist_ok=True)
    arq_registro = raiz / "candidatos.json"
    registro = (json.loads(arq_registro.read_text(encoding="utf-8"))
                if arq_registro.exists() else {})

    for item in plano:
        idn, tipo = item["id"], item.get("tipo", "foto")
        pasta = raiz / "candidatos" / idn
        pasta.mkdir(exist_ok=True)
        print(f"[{idn}] {tipo}: {item['descricao'][:58]}")

        achados: list[dict] = []
        vistos: set[str] = set()
        for nome_acervo in item.get("acervos", ["pixabay"]):
            buscador = acervos.BUSCADORES.get(nome_acervo)
            if not buscador:
                print(f"    ! acervo desconhecido: {nome_acervo}", file=sys.stderr)
                continue
            for termo in item.get("termos", []):
                if len(achados) >= args.por_item:
                    break
                falta = args.por_item - len(achados)
                try:
                    ctx = item.get("contexto")
                    novos = (buscador(termo, tipo, falta, ctx) if nome_acervo == "pixabay"
                             else buscador(termo, falta, ctx))
                except Exception as e:
                    print(f"    ! {nome_acervo} '{termo}': {str(e)[:80]}", file=sys.stderr)
                    novos = []
                for n in novos:
                    chave = n.get("pagina") or n.get("url")
                    if chave in vistos:
                        continue
                    vistos.add(chave)
                    n["termo"] = termo
                    achados.append(n)
                time.sleep(acervos.PAUSA)

        guardados = []
        for n, cand in enumerate(achados[: args.por_item], 1):
            alvo = pasta / f"{cand['acervo']}_{n}.{cand['ext']}"
            if cand.get("remoto"):
                if not _cortar_remoto(cand["url"], alvo, args.duracao, args.inicio_arquivo):
                    continue
            else:
                if not _baixar(cand["url"], alvo):
                    continue
                if tipo == "video":
                    _cortar_local(alvo, args.duracao)
            cand["arquivo"] = str(alvo.relative_to(args.projeto))
            cand.pop("url", None)        # a URL do CDN expira; a página do item fica
            guardados.append(cand)
            print(f"    {n}. {cand['acervo']} — {str(cand.get('licenca', ''))[:46]}")

        if not guardados:
            print("    (vazio — o item exato não apareceu em nenhum acervo)")
        registro[idn] = guardados

    arq_registro.write_text(json.dumps(registro, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    total = sum(len(v) for v in registro.values())
    vazios = sorted(k for k, v in registro.items() if not v)
    print(f"\n{total} candidatos em {len(registro)} itens → {arq_registro}")
    if vazios:
        print(f"SEM RESULTADO ({len(vazios)}): {', '.join(vazios)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
