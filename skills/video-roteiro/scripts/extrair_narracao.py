"""Gera uma versao de narracao pura a partir do roteiro estruturado.

Le o arquivo .md com blocos no formato:

    ### TITULO DO BLOCO

    **Fala:** "Texto falado."

E gera um .txt contendo apenas o texto falado, um paragrafo por bloco,
sem titulos, sem rotulos, sem markdown e sem aspas envolventes.
As aspas francesas internas (« ... ») SÃO preservadas: elas marcam a
entonacao de uma citacao na locucao. Aspas retas (") sao removidas.

Uso:
    python extrair_narracao.py <roteiro.md> [saida.txt]

Se a saida nao for informada, usa o mesmo caminho com .txt.
"""

import re
import sys
from pathlib import Path


def extrair_falas(texto: str) -> list[str]:
    falas: list[str] = []
    for linha in texto.splitlines():
        match = re.match(r"^\*\*Fala\s*:\*\*\s*(.+)$", linha)
        if not match:
            continue
        fala = match.group(1).strip()
        # Remove markdown e as aspas que envolvem a fala inteira.
        fala = fala.replace("**", "").replace("*", "")
        if fala.startswith("\u00ab") and fala.endswith("\u00bb"):
            fala = fala[1:-1].strip()
        # Aspas retas saem; as aspas francesas internas ficam, pois dao
        # a entonacao correta de citacao na locucao.
        fala = fala.replace('"', "")
        fala = re.sub(r"[ \t]{2,}", " ", fala).strip()
        if fala:
            falas.append(fala)
    return falas


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python extrair_narracao.py <roteiro.md> [saida.txt]")
        sys.exit(1)

    entrada = Path(sys.argv[1])
    if not entrada.exists():
        print(f"Erro: arquivo nao encontrado: {entrada}")
        sys.exit(1)

    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else entrada.with_suffix(".txt")
    falas = extrair_falas(entrada.read_text(encoding="utf-8"))

    if not falas:
        print("Erro: nenhuma fala encontrada. Use o formato **Fala:** em cada bloco.")
        sys.exit(1)

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n\n".join(falas) + "\n", encoding="utf-8")
    print(f"OK: {len(falas)} paragrafos de narracao.")
    print(f"Texto: {saida}")


if __name__ == "__main__":
    main()
