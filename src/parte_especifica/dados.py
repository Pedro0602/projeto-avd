# [IA] Claude – carregamento, variáveis derivadas e opções de tratamento do Titanic
"""Funções de dados da Parte Específica (Titanic), usadas pelo notebook de EDA e pelo dashboard."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO_BRUTO = RAIZ / "data" / "parte_especifica" / "Titanic-Dataset.csv"
CAMINHO_TRATADO = RAIZ / "data" / "parte_especifica" / "titanic_tratado.csv"

ALVO = "Survived"

# Agrupamento dos pronomes de tratamento extraídos do nome
MAPA_TITULOS = {
    "Mr": "Mr", "Mrs": "Mrs", "Miss": "Miss", "Master": "Master",
    "Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs",
}

METODOS_AGE = {
    "mediana_global": "Mediana geral de Age",
    "mediana_classe_sexo": "Mediana de Age por Pclass × Sex",
    "mediana_titulo": "Mediana de Age por Title",
}


def carregar_bruto(caminho: Path | str = CAMINHO_BRUTO) -> pd.DataFrame:
    return pd.read_csv(caminho)


def adicionar_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Cria variáveis derivadas sem alterar as originais."""
    df = df.copy()
    titulo = df["Name"].str.extract(r",\s*([^\.]+)\.", expand=False).str.strip()
    df["Title"] = titulo.map(MAPA_TITULOS).fillna("Raro")
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["Deck"] = df["Cabin"].str[0].fillna("Desconhecido")
    df["Cabin_known"] = df["Cabin"].notna().astype(int)
    df["Age_missing"] = df["Age"].isna().astype(int)
    df["TicketGroupSize"] = df.groupby("Ticket")["Ticket"].transform("count")
    return df


def imputar_age(df: pd.DataFrame, metodo: str) -> pd.Series:
    """Retorna Age com os faltantes preenchidos pelo método escolhido (ver METODOS_AGE)."""
    if metodo == "mediana_global":
        return df["Age"].fillna(df["Age"].median())
    if metodo == "mediana_classe_sexo":
        return df["Age"].fillna(df.groupby(["Pclass", "Sex"])["Age"].transform("median"))
    if metodo == "mediana_titulo":
        return df["Age"].fillna(df.groupby("Title")["Age"].transform("median"))
    raise ValueError(f"Método desconhecido: {metodo}. Opções: {list(METODOS_AGE)}")


def tratar(df: pd.DataFrame, metodo_age: str, embarked: str = "moda") -> pd.DataFrame:
    """Aplica o tratamento escolhido pelo grupo. Nenhuma linha é removida.

    - Age: imputação pelo `metodo_age` (a coluna Age_missing guarda quem foi imputado)
    - Cabin: não é imputada; Deck = "Desconhecido" e Cabin_known = 0
    - Embarked: "moda" (porto mais frequente) ou "desconhecido" (categoria própria)
    """
    out = adicionar_derivadas(df) if "Title" not in df.columns else df.copy()
    out["Age"] = imputar_age(out, metodo_age)
    if embarked == "moda":
        out["Embarked"] = out["Embarked"].fillna(out["Embarked"].mode()[0])
    elif embarked == "desconhecido":
        out["Embarked"] = out["Embarked"].fillna("Desconhecido")
    else:
        raise ValueError("embarked deve ser 'moda' ou 'desconhecido'")
    return out


def carregar_tratado(caminho: Path | str = CAMINHO_TRATADO) -> pd.DataFrame:
    return pd.read_csv(caminho)


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
