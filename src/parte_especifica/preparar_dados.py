# [IA] Claude – extrai o train.csv do ZIP da competição para a pasta de dados
"""Prepara o dataset Spaceship Titanic.

As regras da competição não permitem redistribuir os dados, por isso o CSV não fica no repositório.

1. Entre em https://www.kaggle.com/competitions/spaceship-titanic/data e aceite as regras
2. Baixe o ZIP (Download All)
3. Rode: python -m src.parte_especifica.preparar_dados caminho/para/spaceship-titanic.zip
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
