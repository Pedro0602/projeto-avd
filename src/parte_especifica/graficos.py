"""Visualizações oficiais do grupo.

ESTE ARQUIVO É DO GRUPO. Registre aqui as 4 visualizações exploratórias e as 2 explanatórias
que vão para o dashboard (e para o relatório). Cada uma aparece com a sua nota analítica,
lida de `notas/<nota>.md`.

Construtores disponíveis em dash_comum (todos devolvem uma figura Plotly com título, eixos e legenda):
    histograma(df, x, por_situacao=True, percentual=False, log_y=False, titulo=None)
    barras_contagem(df, x, por_situacao=True, titulo=None)
    taxa_transporte(df, x, destacar=None, titulo=None)      # destacar=[...] pinta só essas barras
    taxa_dois_fatores(df, linhas, colunas, titulo=None)
    dispersao(df, x, y, log_y=False, titulo=None)
    boxplot(df, x, y, por_situacao=True, log_y=False, titulo=None)
Também dá para escrever uma função própria que receba o DataFrame e devolva uma figura Plotly.

Colunas do DataFrame: Transported, Situacao, HomePlanet, CryoSleep, Destination, Age, AgeGroup, VIP,
RoomService, FoodCourt, ShoppingMall, Spa, VRDeck, TotalSpend, AnySpend, GroupSize, Solo, Deck,
CabinNum, Side.

Formato de cada entrada:
    Grafico("exp_1", lambda df: <construtor>(df, ...))
"""
# [IA] Claude – estrutura do registro (as entradas das listas são do grupo)
from src.parte_especifica.dash_comum import (  # noqa: F401
    Grafico,
    barras_contagem,
    boxplot,
    dispersao,
    histograma,
    taxa_dois_fatores,
    taxa_ausencia,
    taxa_transporte,
)

EXPLORATORIAS: list[Grafico] = [
    Grafico(
        "exp_1",
        lambda df: barras_contagem(
            df,
            x="Situacao",
            por_situacao=False,
            titulo="Distribuição do resultado de transporte",
        ),
    ),
    Grafico(
        "exp_2",
        lambda df: taxa_transporte(
            df,
            x="Destination",
            titulo="Taxa de transporte por destino",
        ),
    ),
    Grafico(
        "exp_3",
        lambda df: histograma(
            df,
            x="Age",
            percentual=True,
            titulo="Distribuição da idade tratada por resultado",
        ),
    ),
    Grafico(
        "exp_4",
        lambda df: taxa_ausencia(
            df,
            por="Situacao",
            variaveis=["Age", "CryoSleep", "Cabin", "VIP"],
            titulo="Valores ausentes no arquivo original por resultado",
        ),
    ),
]

EXPLANATORIAS: list[Grafico] = [
    Grafico(
        "expl_1",
        lambda df: taxa_dois_fatores(
            df,
            linhas="CryoSleep",
            colunas="HomePlanet",
            titulo="Taxa de transporte por criogenia e planeta de origem",
        ),
    ),
    Grafico(
        "expl_2",
        lambda df: taxa_transporte(
            df,
            x="CryoSleep",
            destacar=["Sim"],
            titulo="Passageiros em criogenia foram transportados com maior frequência",
        ),
    ),
]
