# [IA] Claude – cálculos em cache e gráficos da página da Parte Comum (K-Means / Obesity)
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.parte_comum import kmeans as km

CLASSES = km.ORDEM_CLASSES
CORES_CLASSE = dict(zip(CLASSES, px.colors.sample_colorscale("Viridis", [i / 6 for i in range(7)])))
KS = list(range(2, 11))


@st.cache_data
def preparar(conjunto: str = "numericas"):
    df = km.carregar_dados()
    X, _ = km.preparar_X(df, conjunto)
    proj, var = km.projetar_pca(X)
    curva = km.curva_cotovelo(X, ks=KS)
    return df, X, proj, var, curva


@st.cache_data
def passada(k: int, conjunto: str = "numericas") -> dict:
    df, X, *_ = preparar(conjunto)
    res = km.avaliar_passada(df, X, k)
    res.pop("modelo")
    return res


def fig_cotovelo(curva: pd.DataFrame, k_escolhido: int, k_sugerido: int) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=curva["k"], y=curva["inercia"], mode="lines+markers", name="Inércia",
        line=dict(color="#1f6feb"), hovertemplate="k=%{x}<br>Inércia: %{y:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=k_escolhido, line_dash="dash", line_color="#d1242f",
                  annotation_text=f"k livre = {k_escolhido}", annotation_position="top right")
    if k_sugerido != k_escolhido:
        fig.add_vline(x=k_sugerido, line_dash="dot", line_color="#57606a",
                      annotation_text=f"sugestão automática = {k_sugerido}", annotation_position="bottom left")
    fig.update_layout(title="Método do Cotovelo (variáveis padronizadas)", showlegend=False)
    fig.update_xaxes(title="Número de clusters (k)", dtick=1)
    fig.update_yaxes(title="Inércia (soma das distâncias quadradas)")
    return fig


def fig_transicao(sequencia: list[int | str], conjunto: str = "numericas") -> go.Figure:
    """Animação: cada ponto pintado pela classe majoritária do seu cluster, k a k,
    terminando nas classes reais. As posições (PCA) são fixas; só as cores mudam."""
    df, _, proj, var, _ = preparar(conjunto)
    reais = df[km.ALVO].to_numpy()

    def quadro(passo):
        if passo == "real":
            classes = reais
            nome = "Classes reais"
        else:
            res = passada(passo, conjunto)
            classes = pd.Series(res["clusters"]).map(res["mapa"]).to_numpy()
            nome = f"k = {passo}"
        cores = [CORES_CLASSE[c] for c in classes]
        return nome, go.Scatter(
            x=proj["PC1"], y=proj["PC2"], mode="markers",
            marker=dict(color=cores, size=5, opacity=0.75),
            text=classes, hovertemplate="%{text}<extra></extra>", showlegend=False,
        )

    quadros = [quadro(p) for p in sequencia]
    fig = go.Figure(data=[quadros[0][1]])
    for classe, cor in CORES_CLASSE.items():  # legenda fixa
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=cor, size=10),
                                 name=classe))
    fig.frames = [go.Frame(data=[tr], name=nome, traces=[0]) for nome, tr in quadros]

    anim = dict(mode="immediate", frame=dict(duration=900, redraw=True), transition=dict(duration=500))
    fig.update_layout(
        title=f"Transição entre agrupamentos — {quadros[0][0]} → … → {quadros[-1][0]}",
        legend_title_text="Classe (majoritária do cluster)",
        updatemenus=[dict(
            type="buttons", direction="left", x=0, y=-0.18, xanchor="left", yanchor="top",
            buttons=[
                dict(label="▶ Reproduzir", method="animate", args=[None, {**anim, "fromcurrent": True}]),
                dict(label="⏸ Pausar", method="animate",
                     args=[[None], dict(mode="immediate", frame=dict(duration=0), transition=dict(duration=0))]),
            ],
        )],
        sliders=[dict(
            x=0.25, y=-0.12, len=0.75, currentvalue=dict(prefix="Etapa: "),
            steps=[dict(label=nome, method="animate", args=[[nome], anim]) for nome, _ in quadros],
        )],
        margin=dict(b=120),
        height=620,
    )
    fig.update_xaxes(title=f"PC1 ({var[0]:.1%} da variância)")
    fig.update_yaxes(title=f"PC2 ({var[1]:.1%} da variância)")
    return fig


def fig_matriz(matriz: pd.DataFrame, titulo: str) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=matriz.to_numpy(), x=list(matriz.columns), y=list(matriz.index),
        text=matriz.to_numpy(), texttemplate="%{text}", colorscale="Blues",
        colorbar=dict(title="Pessoas"),
        hovertemplate="Real: %{y}<br>Mapeado: %{x}<br>%{z} pessoas<extra></extra>",
    ))
    fig.update_layout(title=titulo, height=480)
    fig.update_xaxes(title="Classe mapeada (majoritária do cluster)", tickangle=-35)
    fig.update_yaxes(title="Classe real", autorange="reversed")
    return fig


def fig_contingencia(tab: pd.DataFrame, titulo: str) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=tab.to_numpy(), x=list(tab.columns), y=[f"Cluster {i}" for i in tab.index],
        text=tab.to_numpy(), texttemplate="%{text}", colorscale="Blues",
        colorbar=dict(title="Pessoas"),
    ))
    fig.update_layout(title=titulo, height=120 + 45 * len(tab))
    fig.update_xaxes(title="Classe real", tickangle=-35)
    fig.update_yaxes(title="Cluster", autorange="reversed")
    return fig
