# [IA] Claude – funções de padronização, K-Means, mapeamento cluster→classe e métricas
"""Funções da Parte Comum (dataset Obesity).

Uso como script:
    python -m src.parte_comum.kmeans --modo livre --out ./out/parte_comum/
    python -m src.parte_comum.kmeans --modo livre --k 4 --out ./out/parte_comum/
    python -m src.parte_comum.kmeans --modo fixo --out ./out/parte_comum/
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO_CSV = RAIZ / "data" / "parte_comum" / "ObesityDataSet_raw_and_data_sinthetic.csv"

ALVO = "NObeyesdad"
COLUNAS_NUMERICAS = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]

# Ordem das classes do menor para o maior nível de peso (usada nas tabelas e gráficos)
ORDEM_CLASSES = [
    "Insufficient_Weight",
    "Normal_Weight",
    "Overweight_Level_I",
    "Overweight_Level_II",
    "Obesity_Type_I",
    "Obesity_Type_II",
    "Obesity_Type_III",
]
SEMENTE = 42


# ----------------------------------------------------------------------------
# Dados e padronização
# ----------------------------------------------------------------------------
def carregar_dados(caminho: Path | str = CAMINHO_CSV) -> pd.DataFrame:
    return pd.read_csv(caminho)


def padronizar(df: pd.DataFrame, colunas: list[str] = COLUNAS_NUMERICAS):
    """Aplica z-score (média 0, desvio 1) nas colunas escolhidas.

    Retorna (X_padronizado como DataFrame, scaler ajustado).
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(df[colunas])
    return pd.DataFrame(X, columns=colunas, index=df.index), scaler


# ----------------------------------------------------------------------------
# K-Means
# ----------------------------------------------------------------------------
def rodar_kmeans(X: pd.DataFrame | np.ndarray, k: int, semente: int = SEMENTE) -> KMeans:
    modelo = KMeans(n_clusters=k, n_init=10, random_state=semente)
    modelo.fit(X)
    return modelo


def curva_cotovelo(X, ks=range(2, 11), semente: int = SEMENTE) -> pd.DataFrame:
    """Inércia (soma das distâncias quadradas intra-cluster) para cada k."""
    linhas = [{"k": k, "inercia": rodar_kmeans(X, k, semente).inertia_} for k in ks]
    return pd.DataFrame(linhas)


def sugerir_k_cotovelo(curva: pd.DataFrame) -> int:
    """Sugestão automática do 'joelho': ponto da curva mais distante da reta
    que liga o primeiro ao último ponto (curvas normalizadas em [0, 1]).

    É apenas uma referência numérica; a escolha final do k é do grupo.
    """
    x = curva["k"].to_numpy(dtype=float)
    y = curva["inercia"].to_numpy(dtype=float)
    xn = (x - x.min()) / (x.max() - x.min())
    yn = (y - y.min()) / (y.max() - y.min())
    # distância de cada ponto à reta entre (xn[0], yn[0]) e (xn[-1], yn[-1])
    p1, p2 = np.array([xn[0], yn[0]]), np.array([xn[-1], yn[-1]])
    v = p2 - p1
    d = np.abs(v[0] * (yn - p1[1]) - v[1] * (xn - p1[0])) / np.linalg.norm(v)
    return int(x[np.argmax(d)])


def projetar_pca(X, n: int = 2) -> tuple[pd.DataFrame, np.ndarray]:
    """Projeta os dados padronizados em 2 componentes principais para visualizar os grupos.

    Retorna (DataFrame com PC1/PC2, variância explicada por componente).
    """
    pca = PCA(n_components=n, random_state=SEMENTE)
    comp = pca.fit_transform(X)
    cols = [f"PC{i + 1}" for i in range(n)]
    return pd.DataFrame(comp, columns=cols), pca.explained_variance_ratio_


# ----------------------------------------------------------------------------
# Mapeamento cluster → classe e métricas
# ----------------------------------------------------------------------------
def tabela_contingencia(clusters, y) -> pd.DataFrame:
    """Contagem cluster × classe real (k linhas × n_classes colunas; pode ser retangular)."""
    tab = pd.crosstab(pd.Series(clusters, name="cluster"), pd.Series(y, name="classe_real"))
    return tab.reindex(columns=[c for c in ORDEM_CLASSES if c in tab.columns])


def mapear_clusters(clusters, y) -> dict[int, str]:
    """Associa cada cluster à classe real majoritária dentro dele."""
    tab = tabela_contingencia(clusters, y)
    return tab.idxmax(axis=1).to_dict()


def matriz_confusao(y_real, y_mapeado, classes: list[str] = ORDEM_CLASSES) -> pd.DataFrame:
    """Matriz de confusão: linhas = classe real, colunas = rótulo mapeado do cluster."""
    m = pd.crosstab(
        pd.Categorical(y_real, categories=classes),
        pd.Categorical(y_mapeado, categories=classes),
        dropna=False,
    )
    m.index.name = "real"
    m.columns.name = "mapeado"
    return m


def metricas_da_matriz(matriz: pd.DataFrame) -> tuple[float, pd.DataFrame]:
    """Calcula acurácia global e precisão/recall por classe diretamente da matriz.

    precisão(c) = VP / (soma da coluna c)   -> NaN se nenhum cluster foi mapeado para c
    recall(c)   = VP / (soma da linha c)
    """
    m = matriz.to_numpy(dtype=float)
    vp = np.diag(m)
    acuracia = vp.sum() / m.sum()
    soma_col = m.sum(axis=0)
    soma_lin = m.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        precisao = np.where(soma_col > 0, vp / soma_col, np.nan)
        recall = np.where(soma_lin > 0, vp / soma_lin, np.nan)
    por_classe = pd.DataFrame(
        {"precisao": precisao, "recall": recall, "suporte": soma_lin.astype(int)},
        index=matriz.index,
    )
    return float(acuracia), por_classe


def avaliar_passada(df: pd.DataFrame, X, k: int, alvo: str = ALVO) -> dict:
    """Executa uma passada completa: K-Means → mapeamento → matriz → métricas."""
    modelo = rodar_kmeans(X, k)
    clusters = modelo.labels_
    y = df[alvo].to_numpy()
    mapa = mapear_clusters(clusters, y)
    y_mapeado = pd.Series(clusters).map(mapa).to_numpy()
    matriz = matriz_confusao(y, y_mapeado)
    acuracia, por_classe = metricas_da_matriz(matriz)
    return {
        "k": k,
        "modelo": modelo,
        "clusters": clusters,
        "mapa": mapa,
        "contingencia": tabela_contingencia(clusters, y),
        "matriz": matriz,
        "acuracia": acuracia,
        "por_classe": por_classe,
    }


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="K-Means sobre o dataset Obesity")
    parser.add_argument("--modo", choices=["livre", "fixo"], required=True)
    parser.add_argument("--k", type=int, help="k da passada livre (padrão: sugestão do cotovelo)")
    parser.add_argument("--out", default=str(RAIZ / "out" / "parte_comum"))
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = carregar_dados()
    X, _ = padronizar(df)

    if args.modo == "livre":
        curva = curva_cotovelo(X)
        curva.to_csv(out / "cotovelo.csv", index=False)
        k = args.k or sugerir_k_cotovelo(curva)
        print(curva.to_string(index=False))
        print(f"\nk usado na passada livre: {k}")
    else:
        k = df[ALVO].nunique()
        print(f"k fixo (número de classes reais): {k}")

    res = avaliar_passada(df, X, k)
    prefixo = f"passada_{args.modo}"
    res["contingencia"].to_csv(out / f"{prefixo}_contingencia.csv")
    res["matriz"].to_csv(out / f"{prefixo}_matriz_confusao.csv")
    res["por_classe"].to_csv(out / f"{prefixo}_metricas_por_classe.csv")
    pd.DataFrame({"cluster": res["clusters"]}).to_csv(out / f"{prefixo}_clusters.csv", index=False)

    print(f"\nMapeamento cluster -> classe: {res['mapa']}")
    print(f"Acurácia: {res['acuracia']:.3f}")
    print(res["por_classe"].round(3).to_string())


if __name__ == "__main__":
    main()
