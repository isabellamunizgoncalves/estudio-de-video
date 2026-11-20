#!/usr/bin/env python3
"""Lê e muda o estado de um vídeo (_CLAUDE/projeto.json) sem abrir o arquivo inteiro.

Uso:
  estado.py <pasta> status
  estado.py <pasta> <bloco> [--json]
  estado.py <pasta> --item <id>
  estado.py <pasta> --set <caminho.com.pontos> <valor>     (valor em JSON; se não for JSON, vira texto)
  estado.py <pasta> --etapa <etapa>=<status>
  estado.py <pasta> --pendencia <etapa> "<texto>"
  estado.py <pasta> --resolver <id>
  estado.py <pasta> --criar <nome-do-projeto>              (cria o projeto.json inicial)
"""
import json
import os
import sys
import tempfile
from datetime import date

ETAPAS = ["iniciar", "preparar", "mapa", "imagens", "animar", "som", "final"]
STATUS = {"pendente", "em_andamento", "aguardando_aprovacao", "aguardando_isabella", "concluido", "nao_precisa"}
LISTAS_COM_ID = ["capitulos", "cenas", "imagens", "musica", "sfx", "renders", "eventos_som", "pendencias", "divergencias"]


def caminho(pasta):
    return os.path.join(pasta, "_CLAUDE", "projeto.json")


def ler(pasta):
    p = caminho(pasta)
    if not os.path.exists(p):
        sys.exit(f"Sem projeto: {p} não existe. Rode a /video-iniciar.")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def gravar(pasta, dados):
    p = caminho(pasta)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def criar(pasta, nome):
    if os.path.exists(caminho(pasta)):
        sys.exit("projeto.json já existe: nada foi sobrescrito.")
    dados = {
        "projeto": nome,
        "criado_em": date.today().isoformat(),
        "perfil": "retrovisage",
        "formato": {"largura": 1920, "altura": 1080, "fps": 30},
        "ferramentas": {},
        "etapas": {e: "pendente" for e in ETAPAS},
        "capitulos": [],
        "pendencias": [],
    }
    dados["etapas"]["iniciar"] = "em_andamento"
    gravar(pasta, dados)
    print(f"Criado {caminho(pasta)}")


def resumo_item(it):
    partes = [str(it.get("id", "?"))]
    for k in ("status", "inicio", "fim", "titulo", "texto", "descricao", "conceito", "arquivo", "etapa"):
        if k in it and it[k] not in (None, ""):
            v = it[k]
            if isinstance(v, float):
                v = f"{v:.2f}"
            v = str(v)
            partes.append(v if len(v) <= 70 else v[:67] + "...")
    return " · ".join(partes)


def status(pasta):
    d = ler(pasta)
    print(f"Projeto: {d.get('projeto')} · perfil {d.get('perfil')}")
    for e in ETAPAS:
        print(f"  {e:<9} {d['etapas'].get(e, 'pendente')}")
    trechos = d.get("trechos") or {}
    if trechos:
        print("Trechos:")
        for nome, t in trechos.items():
            print(f"  {nome}: {t.get('status', '?')}")
    pend = [p for p in d.get("pendencias", []) if not p.get("resolvida")]
    print(f"Pendências: {len(pend)}")
    for p in pend:
        print(f"  {p['id']} [{p['etapa']}] {p['texto']}")
    for a in alertas(d):
        print(f"ALERTA: {a}")
    apr = os.path.join(pasta, "_CLAUDE", "aprendizados.md")
    if os.path.exists(apr):
        with open(apr, encoding="utf-8") as f:
            n = sum(1 for linha in f if linha.startswith("- [ ]"))
        print(f"Aprendizados anotados (não aplicados): {n}")


def alertas(d):
    out = []
    v = d.get("versoes", {})
    narr, mapa = v.get("narracao"), v.get("mapa_feito_sobre_narracao")
    if narr and mapa and narr != mapa:
        out.append(f"a narração mudou (v{narr}) depois do mapa (feito sobre v{mapa}): mapa e animações precisam ser recalculados")
    return out


def bloco(pasta, nome, como_json):
    d = ler(pasta)
    if nome not in d:
        sys.exit(f"Bloco '{nome}' não existe. Blocos: {', '.join(d.keys())}")
    b = d[nome]
    if como_json or not isinstance(b, list):
        print(json.dumps(b, ensure_ascii=False, indent=2))
        return
    for it in b:
        print(resumo_item(it) if isinstance(it, dict) else it)
    print(f"({len(b)} itens)")


def achar_item(d, ident):
    for k in LISTAS_COM_ID:
        for it in d.get(k, []) or []:
            if isinstance(it, dict) and it.get("id") == ident:
                return k, it
    return None, None


def set_caminho(pasta, cam, valor):
    d = ler(pasta)
    try:
        valor = json.loads(valor)
    except (json.JSONDecodeError, TypeError):
        pass
    alvo = d
    partes = cam.split(".")
    for p in partes[:-1]:
        alvo = alvo.setdefault(p, {})
    alvo[partes[-1]] = valor
    gravar(pasta, d)
    print(f"{cam} = {json.dumps(valor, ensure_ascii=False)}")


def main(a):
    if len(a) < 2:
        sys.exit(__doc__)
    pasta, cmd = a[0], a[1]
    if cmd == "status":
        status(pasta)
    elif cmd == "--criar":
        criar(pasta, a[2])
    elif cmd == "--item":
        k, it = achar_item(ler(pasta), a[2])
        if not it:
            sys.exit(f"Item {a[2]} não encontrado.")
        print(f"[{k}]")
        print(json.dumps(it, ensure_ascii=False, indent=2))
    elif cmd == "--set":
        set_caminho(pasta, a[2], a[3])
    elif cmd == "--etapa":
        etapa, st = a[2].split("=", 1)
        if etapa not in ETAPAS or st not in STATUS:
            sys.exit(f"Etapa ou status inválido. Etapas: {ETAPAS}. Status: {sorted(STATUS)}")
        d = ler(pasta)
        d["etapas"][etapa] = st
        gravar(pasta, d)
        print(f"{etapa} = {st}")
    elif cmd == "--pendencia":
        d = ler(pasta)
        ps = d.setdefault("pendencias", [])
        n = max([int(p["id"][1:]) for p in ps] + [0]) + 1
        p = {"id": f"p{n:02d}", "etapa": a[2], "texto": a[3], "resolvida": False}
        ps.append(p)
        gravar(pasta, d)
        print(f"Pendência {p['id']} anotada.")
    elif cmd == "--resolver":
        d = ler(pasta)
        for p in d.get("pendencias", []):
            if p["id"] == a[2]:
                p["resolvida"] = True
                gravar(pasta, d)
                print(f"{a[2]} resolvida.")
                return
        sys.exit(f"Pendência {a[2]} não encontrada.")
    else:
        bloco(pasta, cmd, "--json" in a)


if __name__ == "__main__":
    main(sys.argv[1:])