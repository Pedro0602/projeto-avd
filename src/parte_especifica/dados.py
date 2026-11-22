# [IA] Claude – carregamento, variáveis derivadas e opções de tratamento do Spaceship Titanic
"""Funções de dados da Parte Específica (Spaceship Titanic), usadas pelo notebook e pelo dashboard."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO_BRUTO = RAIZ / "data" / "parte_especifica" / "spaceship_train.csv"
CAMINHO_TRATADO = RAIZ / "data" / "parte_especifica" / "spaceship_tratado.csv"

ALVO = "Transported"
GASTOS = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
COLUNAS_COM_FALTANTES = ["HomePlanet", "CryoSleep", "Cabin", "Destination", "Age", "VIP", *GASTOS, "Name"]
DESCONHECIDO = "Desconhecido"

METODOS_AGE = {
    "mediana_global": "Mediana geral de Age",
    "mediana_planeta": "Mediana de Age por HomePlanet",
    "mediana_planeta_cryo": "Mediana de Age por HomePlanet × CryoSleep",
}

FAIXAS_IDADE = ["0-12", "13-17", "18-25", "26-40", "41-60", "61+"]


def carregar_bruto(caminho: Path | str = CAMINHO_BRUTO) -> pd.DataFrame:
    if not Path(caminho).exists():
        raise FileNotFoundError(
            "Dataset não encontrado. Baixe o ZIP no Kaggle e rode: "
            "python -m src.parte_especifica.preparar_dados <caminho do spaceship-titanic.zip>"
        )
    return pd.read_csv(caminho)


def _faixa_idade(idade: pd.Series) -> pd.Series:
    faixa = pd.cut(idade, bins=[-1, 12, 17, 25, 40, 60, 200], labels=FAIXAS_IDADE)
    return faixa.astype(object).where(faixa.notna(), DESCONHECIDO)


def adicionar_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Cria variáveis derivadas e indicadores de ausência, sem alterar as colunas originais."""
    df = df.copy()
    df["Group"] = df["PassengerId"].str.split("_").str[0]
    df["GroupSize"] = df.groupby("Group")["Group"].transform("size")
    df["Solo"] = np.where(df["GroupSize"] == 1, "Sim", "Não")

    cabine = df["Cabin"].str.split("/", expand=True)
    df["Deck"] = cabine[0].fillna(DESCONHECIDO)
    df["CabinNum"] = pd.to_numeric(cabine[1], errors="coerce")
    df["Side"] = cabine[2].map({"P": "Bombordo", "S": "Estibordo"}).fillna(DESCONHECIDO)

    for col in COLUNAS_COM_FALTANTES:
        df[f"Falt_{col}"] = df[col].isna().astype(int)
    df["N_faltantes"] = df[[f"Falt_{c}" for c in COLUNAS_COM_FALTANTES]].sum(axis=1)

    df["TotalSpend"] = df[GASTOS].sum(axis=1, min_count=1)
    df["AgeGroup"] = _faixa_idade(df["Age"])
    return df


def aplicar_regras_logicas(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Preenche faltantes deduzíveis das outras colunas. Retorna (df, contagem por regra).

    - CryoSleep = True -> gastos ausentes = 0 (passageiro confinado à cabine)
    - Age <= 12 -> gastos ausentes = 0 (nenhuma criança registrada tem gasto)
    - CryoSleep ausente e algum gasto > 0 -> CryoSleep = False
    - HomePlanet ausente -> planeta de outro integrante do mesmo grupo, quando conhecido
    """
    df = df.copy()
    contagem: dict[str, int] = {}

    cryo = df["CryoSleep"].eq(True)
    contagem["Gastos = 0 por CryoSleep"] = int(df.loc[cryo, GASTOS].isna().sum().sum())
    df.loc[cryo, GASTOS] = df.loc[cryo, GASTOS].fillna(0)

    crianca = df["Age"].le(12)
    contagem["Gastos = 0 por idade <= 12"] = int(df.loc[crianca, GASTOS].isna().sum().sum())
    df.loc[crianca, GASTOS] = df.loc[crianca, GASTOS].fillna(0)

    gastou = df[GASTOS].fillna(0).sum(axis=1) > 0
    regra = df["CryoSleep"].isna() & gastou
    contagem["CryoSleep = False por ter gasto"] = int(regra.sum())
    df["CryoSleep"] = df["CryoSleep"].astype(object)
    df.loc[regra, "CryoSleep"] = False

    planeta_grupo = df.groupby("Group")["HomePlanet"].transform("first")
    regra = df["HomePlanet"].isna() & planeta_grupo.notna()
    contagem["HomePlanet pelo grupo"] = int(regra.sum())
    df.loc[regra, "HomePlanet"] = planeta_grupo[regra]
    return df, contagem


def imputar_age(df: pd.DataFrame, metodo: str) -> pd.Series:
    """Retorna Age com os faltantes preenchidos pelo método escolhido (ver METODOS_AGE)."""
    geral = df["Age"].median()
    if metodo == "mediana_global":
        return df["Age"].fillna(geral)
    if metodo == "mediana_planeta":
        chaves = [df["HomePlanet"].fillna(DESCONHECIDO)]
    elif metodo == "mediana_planeta_cryo":
        chaves = [df["HomePlanet"].fillna(DESCONHECIDO), df["CryoSleep"].astype(object).fillna(DESCONHECIDO).astype(str)]
    else:
        raise ValueError(f"Método desconhecido: {metodo}. Opções: {list(METODOS_AGE)}")
    return df["Age"].fillna(df.groupby(chaves)["Age"].transform("median")).fillna(geral)


def tratar(df: pd.DataFrame, metodo_age: str, categoricas: str = "desconhecido",
           regras: bool = True) -> pd.DataFrame:
    """Aplica o tratamento escolhido pelo grupo. Nenhuma linha é removida.

    - regras=True: aplica primeiro as deduções de `aplicar_regras_logicas`
    - Age: imputação por `metodo_age` (Falt_Age guarda quem foi imputado)
    - Gastos restantes: mediana de cada coluna
    - HomePlanet, CryoSleep, Destination, VIP: "desconhecido" (categoria própria) ou "moda"
    - Cabin: não é imputada; Deck e Side ficam "Desconhecido"
    """
    if categoricas not in ("desconhecido", "moda"):
        raise ValueError("categoricas deve ser 'desconhecido' ou 'moda'")
    out = adicionar_derivadas(df) if "Group" not in df.columns else df.copy()
    if regras:
        out, _ = aplicar_regras_logicas(out)
    out["Age"] = imputar_age(out, metodo_age)
    out[GASTOS] = out[GASTOS].fillna(out[GASTOS].median())

    for col in ("HomePlanet", "CryoSleep", "Destination", "VIP"):
        valor = out[col].mode()[0] if categoricas == "moda" else DESCONHECIDO
        out[col] = out[col].astype(object).where(out[col].notna(), valor)
    for col in ("CryoSleep", "VIP"):
        out[col] = out[col].map({True: "Sim", False: "Não", DESCONHECIDO: DESCONHECIDO})

    out["TotalSpend"] = out[GASTOS].sum(axis=1)
    out["AnySpend"] = np.where(out["TotalSpend"] > 0, "Sim", "Não")
    out["AgeGroup"] = _faixa_idade(out["Age"])
    out[ALVO] = out[ALVO].astype(int)
    return out


def carregar_tratado(caminho: Path | str = CAMINHO_TRATADO) -> pd.DataFrame:
    return pd.read_csv(caminho, dtype={"Group": str}, keep_default_na=True, na_values=[""])


def limites_iqr(s: pd.Series, fator: float = 1.5) -> tuple[float, float]:
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - fator * iqr, q3 + fator * iqr


def cramers_v(a: pd.Series, b: pd.Series) -> float:
    tab = pd.crosstab(a, b).to_numpy(dtype=float)
    n = tab.sum()
    esperado = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / n
    qui2 = ((tab - esperado) ** 2 / esperado).sum()
    r, k = tab.shape
    return float(np.sqrt(qui2 / (n * (min(r, k) - 1)))) if min(r, k) > 1 else np.nan
