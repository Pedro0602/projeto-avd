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
    taxa_transporte,
)

EXPLORATORIAS: list[Grafico] = [
    # Grafico("exp_1", lambda df: ...),
    # Grafico("exp_2", lambda df: ...),
    # Grafico("exp_3", lambda df: ...),
    # Grafico("exp_4", lambda df: ...),
]

EXPLANATORIAS: list[Grafico] = [
    # Grafico("expl_1", lambda df: ...),
    # Grafico("expl_2", lambda df: ...),
]
