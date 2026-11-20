#!/usr/bin/env python3
"""Gera index.html a partir de index.tpl (modelo com marcador), embutindo as fontes (CSS embutido, nunca <link>).
Uso: python3 montar_html.py <pasta-do-projeto-hyperframes>
Troca o marcador /*FONTES*/ pelo conteúdo de fontes.css da pasta."""
import os, sys
p = sys.argv[1]
src = open(os.path.join(p, "index.tpl"), encoding="utf-8").read()
fontes = open(os.path.join(p, "fontes.css"), encoding="utf-8").read()
open(os.path.join(p, "index.html"), "w", encoding="utf-8").write(src.replace("/*FONTES*/", fontes))
print("index.html montado")