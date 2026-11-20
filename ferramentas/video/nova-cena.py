#!/usr/bin/env python3
"""
Cria uma nova cena a partir do template global (formato 16:9 YouTube).
Uso: python ferramentas/nova-cena.py <pasta-destino> <nome-cena>
Ex: python ferramentas/nova-cena.py v02 cena-intro
"""
import json
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "templates" / "cena-template.hyperframes.json"
GLOBAL_CONFIG = ROOT / "config" / "formato-global.json"

def main():
    if len(sys.argv) < 3:
        print("Uso: python nova-cena.py <pasta-destino> <nome-cena>")
        print("Ex: python nova-cena.py v02 cena-intro")
        sys.exit(1)

    pasta_destino = ROOT / sys.argv[1]
    nome_cena = sys.argv[2]

    if not pasta_destino.exists():
        pasta_destino.mkdir(parents=True)
        print(f"📁 Pasta criada: {pasta_destino}")

    # Carrega template
    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        cena = json.load(f)

    # Atualiza nome
    cena["nome"] = nome_cena

    # Salva nova cena
    arquivo_saida = pasta_destino / f"{nome_cena}.hyperframes.json"
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(cena, f, indent=2, ensure_ascii=False)

    print(f"✅ Cena criada: {arquivo_saida}")
    print(f"   Formato: 1920x1080 (16:9 YouTube) - herdado do config global")
    print(f"   Edite o JSON e adicione assets em {pasta_destino}/pecas/")

    # Cria pastas de assets
    (pasta_destino / "pecas").mkdir(exist_ok=True)
    (pasta_destino / "imagens").mkdir(exist_ok=True)
    print(f"   Pastas de assets criadas: pecas/, imagens/")

if __name__ == "__main__":
    main()