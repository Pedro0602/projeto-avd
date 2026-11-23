# [IA] Claude – extrai o train.csv do ZIP da competição para a pasta de dados
"""Prepara o dataset Spaceship Titanic.

Use este utilitário quando o CSV local não estiver disponível.

1. Baixe o ZIP em https://www.kaggle.com/competitions/spaceship-titanic/data
2. Rode: python -m src.parte_especifica.preparar_dados caminho/para/spaceship-titanic.zip
"""
import argparse
import zipfile

from src.parte_especifica.dados import CAMINHO_BRUTO


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai o train.csv do Spaceship Titanic")
    parser.add_argument("zip", help="caminho do spaceship-titanic.zip baixado do Kaggle")
    args = parser.parse_args()

    CAMINHO_BRUTO.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip) as zf:
        CAMINHO_BRUTO.write_bytes(zf.read("train.csv"))
    print(f"Salvo em {CAMINHO_BRUTO}")


if __name__ == "__main__":
    main()
