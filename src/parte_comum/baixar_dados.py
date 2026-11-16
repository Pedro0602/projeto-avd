# [IA] Claude – script de download do dataset Obesity (UCI 544)
"""Baixa o dataset Obesity da UCI e salva o CSV em data/parte_comum/."""
import io
import urllib.request
import zipfile
from pathlib import Path

URL = (
    "https://archive.ics.uci.edu/static/public/544/"
    "estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition.zip"
)
DESTINO = Path(__file__).resolve().parents[2] / "data" / "parte_comum"


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL) as resp:
        conteudo = resp.read()
    with zipfile.ZipFile(io.BytesIO(conteudo)) as zf:
        for nome in zf.namelist():
            if nome.lower().endswith(".csv"):
                caminho = DESTINO / Path(nome).name
                caminho.write_bytes(zf.read(nome))
                print(f"Salvo em {caminho}")


if __name__ == "__main__":
    main()
