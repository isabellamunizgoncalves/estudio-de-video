#!/usr/bin/env python3
"""Compara a transcrição com o roteiro e põe a grafia do roteiro nos tempos da transcrição.

Uso: python3 conferir_roteiro.py <pasta-do-video> [roteiro.md]

Lê   _CLAUDE/transcricao/palavras.json e Roteiro/roteiro.md (ou o arquivo dado)
Gera _CLAUDE/transcricao/roteiro_tempos.json  [{"w": palavra do roteiro, "ini", "fim", "frase", "par"}]
     _CLAUDE/transcricao/divergencias.json    [{"tipo", "roteiro", "falado", "tempo"}]
     _CLAUDE/transcricao/frases.md             uma frase por linha, com o tempo (para o Claude ler)

Números e algarismos romanos viram palavras dos dois lados antes de comparar
("1962" = "mil novecentos e sessenta e dois"; "século XIX" = "século dezenove").
"""
import difflib
import json
import os
import re
import sys
import unicodedata

UN = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis dezessete dezoito dezenove".split()
DEZ = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
CEN = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()


def extenso(n):
    if n < 20:
        return UN[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DEZ[d] + ("" if u == 0 else " e " + UN[u])
    if n == 100:
        return "cem"
    if n < 1000:
        c, r = divmod(n, 100)
        return CEN[c] + ("" if r == 0 else " e " + extenso(r))
    if n < 1000000:
        m, r = divmod(n, 1000)
        txt = "mil" if m == 1 else extenso(m) + " mil"
        if r == 0:
            return txt
        return txt + (" e " if r < 100 or r % 100 == 0 else " ") + extenso(r)
    return str(n)


UN_FR = "zero un deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize dix-sept dix-huit dix-neuf".split()
DIZ_FR = {2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante"}


def extenso_fr(n):
    """Números por extenso em francês (as palavras com hífen viram tokens separados depois)."""
    if n < 20:
        return UN_FR[n]
    if n < 70:
        d, u = divmod(n, 10)
        return DIZ_FR[d] + ("" if u == 0 else (" et un" if u == 1 else "-" + UN_FR[u]))
    if n < 80:
        return "soixante" + (" et onze" if n == 71 else "-" + UN_FR[n - 60])
    if n < 100:
        r = n - 80
        return "quatre-vingts" if r == 0 else "quatre-vingt-" + UN_FR[r]
    if n < 1000:
        c, r = divmod(n, 100)
        base = "cent" if c == 1 else UN_FR[c] + (" cents" if r == 0 else " cent")
        return base if r == 0 else base + " " + extenso_fr(r)
    if n < 1000000:
        m, r = divmod(n, 1000)
        base = "mille" if m == 1 else extenso_fr(m) + " mille"
        return base if r == 0 else base + " " + extenso_fr(r)
    return str(n)


IDIOMA = "pt"


ROMANOS = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}


def romano(t):
    if not re.fullmatch(r"[ivxlc]+", t) or t in ("i", "v", "c", "l"):  # letras soltas são palavras
        return None
    total, ant = 0, 0
    for ch in reversed(t):
        v = ROMANOS[ch]
        total = total - v if v < ant else total + v
        ant = max(ant, v)
    return total


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def tokens_norm(palavra):
    """Uma palavra original -> lista de tokens normalizados (números viram várias palavras)."""
    out = []
    # Hífen separa ("Costuma-se" = "Costuma -se"); o resto da pontuação some.
    for parte in re.split("[-‐–'’]", sem_acento(palavra.lower())):
        t = re.sub(r"[^\w]", "", parte)
        if not t:
            continue
        if t.isdigit():
            ext = extenso_fr(int(t)) if IDIOMA == "fr" else extenso(int(t))
            out += [w for w in re.split(r"[\s-]+", sem_acento(ext)) if w]
        elif romano(t):
            ext = extenso_fr(romano(t)) if IDIOMA == "fr" else extenso(romano(t))
            out += [w for w in re.split(r"[\s-]+", sem_acento(ext)) if w]
        else:
            out.append(t)
    return out


def fonetico_fr(s):
    """Aproximação do som em francês: tira letras finais mudas e grafias equivalentes.
    Serve só para classificar divergência (lampes = lampe, tenaient = tenait, on = ont)."""
    s = sem_acento(s.lower()).replace("œ", "oe").replace("æ", "ae")
    out = []
    for w in re.findall(r"[a-z0-9]+", s):
        w = w.replace("y", "i").replace("ph", "f").replace("qu", "k").replace("c", "k")
        w = re.sub(r"(ent|es|ez|er|ait|aient|ai|et|e|s|x|t|d)$", "", w) or w
        w = re.sub(r"(.)\1+", r"\1", w)
        out.append(w)
    return " ".join(x for x in out if x)


def so_grafia(a, b):
    """Diferença só de escrita (papillotes x papilotes): iguais sem acento, sem pontuação
    e com letras dobradas reduzidas. Rigoroso de propósito: provação x aprovação NÃO passa."""
    def base(s):
        s = re.sub(r"\W", "", sem_acento(s.lower()))
        return re.sub(r"(.)\1+", r"\1", s)
    return base(a) == base(b)


def ler_roteiro(caminho):
    with open(caminho, encoding="utf-8") as f:
        texto = f.read()
    pars = [p.strip() for p in re.split(r"\n\s*\n|\n", texto) if p.strip() and not p.startswith("#")]
    palavras = []
    for ip, par in enumerate(pars):
        frases = re.split(r"(?<=[.!?:])\s+", par)
        for fr in frases:
            for w in re.findall(r"\S+", fr):
                palavras.append({"w": w, "par": ip, "frase_txt": fr})
    # id de frase sequencial
    fid, ult = -1, None
    for p in palavras:
        chave = (p["par"], p["frase_txt"])
        if chave != ult:
            fid, ult = fid + 1, chave
        p["frase"] = fid
    return palavras


def main():
    global IDIOMA
    pasta = sys.argv[1]
    try:
        IDIOMA = json.load(open(os.path.join(pasta, "_CLAUDE", "projeto.json"))).get("idioma", "pt")
    except (OSError, ValueError):
        pass
    rot = sys.argv[2] if len(sys.argv) > 2 else os.path.join(pasta, "Roteiro", "roteiro.md")
    d = os.path.join(pasta, "_CLAUDE", "transcricao")
    with open(os.path.join(d, "palavras.json"), encoding="utf-8") as f:
        fal = json.load(f)
    roteiro = ler_roteiro(rot)

    # Expande em tokens normalizados, lembrando de qual palavra veio cada token.
    rt, rt_src = [], []
    for i, p in enumerate(roteiro):
        for t in tokens_norm(p["w"]):
            rt.append(t); rt_src.append(i)
    ft, ft_src = [], []
    for i, p in enumerate(fal):
        for t in tokens_norm(p["w"]):
            ft.append(t); ft_src.append(i)

    sm = difflib.SequenceMatcher(a=rt, b=ft, autojunk=False)
    tempo_tok = [None] * len(rt)
    div = []
    for tag, a1, a2, b1, b2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(a2 - a1):
                tempo_tok[a1 + k] = ft_src[b1 + k]
        else:
            falado = " ".join(fal[i]["w"] for i in sorted(set(ft_src[b1:b2])))
            escrito = " ".join(roteiro[i]["w"] for i in sorted(set(rt_src[a1:a2])))
            t = fal[ft_src[b1]]["ini"] if b1 < b2 else (fal[ft_src[b1 - 1]]["fim"] if b1 > 0 else 0)
            if tag == "replace":
                for k in range(min(a2 - a1, b2 - b1)):  # tempo aproximado para palavras trocadas
                    tempo_tok[a1 + k] = ft_src[b1 + k]
            tipo = {"replace": "trocada", "delete": "faltou na voz", "insert": "a mais na voz"}[tag]
            if tag == "replace" and (so_grafia(escrito, falado) or (IDIOMA == "fr" and fonetico_fr(escrito) == fonetico_fr(falado))):
                tipo = "so_grafia"  # não é erro da voz: só a transcrição escreveu diferente
            div.append({"tipo": tipo, "roteiro": escrito, "falado": falado, "tempo": round(t, 2)})

    # Tempo de cada palavra do roteiro = do primeiro ao último token alinhado.
    out = []
    for i, p in enumerate(roteiro):
        idx = [tempo_tok[k] for k, s in enumerate(rt_src) if s == i and tempo_tok[k] is not None]
        ini = fal[min(idx)]["ini"] if idx else None
        fim = fal[max(idx)]["fim"] if idx else None
        out.append({"w": p["w"], "ini": ini, "fim": fim, "frase": p["frase"], "par": p["par"]})
    # Palavras sem tempo herdam da vizinha (para não quebrar scripts).
    for i, p in enumerate(out):
        if p["ini"] is None:
            ant = next((out[j]["fim"] for j in range(i - 1, -1, -1) if out[j]["fim"] is not None), 0.0)
            prox = next((out[j]["ini"] for j in range(i + 1, len(out)) if out[j]["ini"] is not None), ant)
            p["ini"], p["fim"], p["sem_tempo"] = ant, prox, True

    with open(os.path.join(d, "roteiro_tempos.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    with open(os.path.join(d, "divergencias.json"), "w", encoding="utf-8") as f:
        json.dump(div, f, ensure_ascii=False, indent=1)
    escrever_frases(out, os.path.join(d, "frases.md"))
    reais = [x for x in div if x["tipo"] != "so_grafia"]
    print(f"{len(out)} palavras do roteiro com tempo · {len(reais)} divergências "
          f"(+{len(div) - len(reais)} só de grafia, ignoradas)")
    for x in reais:
        print(f"  {mmss(x['tempo'])} {x['tipo']}: roteiro «{x['roteiro']}» / voz «{x['falado']}»")


def mmss(s):
    return f"{int(s // 60)}:{s % 60:05.2f}"


def escrever_frases(palavras, destino):
    linhas, atual = ["# Narração por frase (tempo da narração usada)", ""], []
    for i, p in enumerate(palavras):
        atual.append(p)
        fim_frase = i == len(palavras) - 1 or palavras[i + 1]["frase"] != p["frase"]
        if fim_frase:
            ini, fim = atual[0]["ini"], atual[-1]["fim"]
            prox = palavras[i + 1]["ini"] if i + 1 < len(palavras) else None
            pausa = f" · pausa {prox - fim:.2f}s" if prox is not None else ""
            novo_par = i + 1 < len(palavras) and palavras[i + 1]["par"] != p["par"]
            linhas.append(f"[{mmss(ini)}–{mmss(fim)}] f{p['frase']:03d} {' '.join(x['w'] for x in atual)}{pausa}")
            if novo_par:
                linhas.append("")
            atual = []
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    main()