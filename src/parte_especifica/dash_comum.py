# [IA] Claude – dados, filtros, notas e construtores de gráficos compartilhados pelo dashboard
"""Funções compartilhadas pelas páginas do dashboard (Parte Específica — Spaceship Titanic)."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.parte_especifica import dados as dd  # noqa: E402

NOTAS = Path(__file__).resolve().parent / "notas"
MARCA_PENDENTE = "PENDENTE"

# ----------------------------------------------------------------------------
# Rótulos, ordens e cores
# ----------------------------------------------------------------------------
ROTULO_ALVO = {0: "Não transportado", 1: "Transportado"}
CORES_ALVO = {"Não transportado": "#9aa5b1", "Transportado": "#1f6feb"}
COR_NEUTRA = "#c3cad3"
COR_DESTAQUE = "#1f6feb"

ROTULOS = {
    "Transported": "Transportado (0/1)",
    "Situacao": "Situação",
    "HomePlanet": "Planeta de origem",
    "CryoSleep": "Sono criogênico",
    "Destination": "Destino",
    "Age": "Idade (anos)",
    "AgeGroup": "Faixa etária",
    "VIP": "VIP",
    "RoomService": "Gasto em serviço de quarto",
    "FoodCourt": "Gasto na praça de alimentação",
    "ShoppingMall": "Gasto no shopping",
    "Spa": "Gasto no spa",
    "VRDeck": "Gasto no deck de realidade virtual",
    "TotalSpend": "Gasto total",
    "AnySpend": "Gastou a bordo",
    "GroupSize": "Tamanho do grupo",
    "Solo": "Viaja sozinho",
    "Deck": "Deck da cabine",
    "CabinNum": "Número da cabine",
    "Side": "Lado da nave",
    "taxa": "Taxa de transporte",
    "n": "Nº de passageiros",
}

NUMERICAS = ["Age", "RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck", "TotalSpend", "GroupSize", "CabinNum"]
CATEGORICAS = ["Situacao", "HomePlanet", "CryoSleep", "Destination", "VIP", "Deck", "Side", "AgeGroup", "Solo", "AnySpend"]

D = dd.DESCONHECIDO
ORDENS = {
    "Situacao": ["Não transportado", "Transportado"],
    "HomePlanet": ["Earth", "Europa", "Mars", D],
    "CryoSleep": ["Não", "Sim", D],
    "Destination": ["TRAPPIST-1e", "55 Cancri e", "PSO J318.5-22", D],
    "VIP": ["Não", "Sim", D],
    "Deck": ["A", "B", "C", "D", "E", "F", "G", "T", D],
    "Side": ["Bombordo", "Estibordo", D],
    "AgeGroup": dd.FAIXAS_IDADE,
    "Solo": ["Não", "Sim"],
    "AnySpend": ["Não", "Sim"],
}

FORMATO_OPCOES = {
    "HomePlanet": {"Earth": "Terra", "Europa": "Europa", "Mars": "Marte"},
}


def rotulo(col: str) -> str:
    return ROTULOS.get(col, col)


def formatar(col: str, valor) -> str:
    """Rótulo legível de uma categoria (ex.: HomePlanet 'Earth' -> 'Terra')."""
    return FORMATO_OPCOES.get(col, {}).get(str(valor), str(valor))


# ----------------------------------------------------------------------------
# Dados
# ----------------------------------------------------------------------------
@st.cache_data
def carregar() -> pd.DataFrame:
    """Dataset tratado, com colunas prontas para exibição."""
    if dd.CAMINHO_TRATADO.exists():
        df = dd.carregar_tratado()
    else:
        df = dd.tratar(dd.carregar_bruto(), "mediana_planeta")
    df["Situacao"] = df["Transported"].map(ROTULO_ALVO)
    return df


# ----------------------------------------------------------------------------
# Filtros globais (barra lateral), persistentes entre páginas
# ----------------------------------------------------------------------------
FILTROS_PILLS = {
    "f_planeta": ("Planeta de origem", "HomePlanet"),
    "f_cryo": ("Sono criogênico", "CryoSleep"),
    "f_destino": ("Destino", "Destination"),
    "f_vip": ("VIP", "VIP"),
}


def _iniciar(key: str, padrao) -> None:
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get(f"_{key}", padrao)


def _guardar(key: str) -> None:
    st.session_state[f"_{key}"] = st.session_state[key]


def _limpar_filtros(idade_padrao: tuple[float, float]) -> None:
    for key, (_, col) in FILTROS_PILLS.items():
        st.session_state[key] = st.session_state[f"_{key}"] = ORDENS[col]
    st.session_state["f_idade"] = st.session_state["_f_idade"] = idade_padrao


def filtros_sidebar(df: pd.DataFrame) -> None:
    idade_padrao = (float(df["Age"].min()), float(df["Age"].max()))
    with st.sidebar:
        st.subheader("Filtros", anchor=False)
        for key, (titulo, col) in FILTROS_PILLS.items():
            _iniciar(key, ORDENS[col])
            st.pills(
                titulo,
                ORDENS[col],
                selection_mode="multi",
                key=key,
                format_func=lambda v, c=col: formatar(c, v),
                on_change=_guardar,
                args=(key,),
            )
        _iniciar("f_idade", idade_padrao)
        st.slider(
            "Idade (anos)",
            min_value=idade_padrao[0],
            max_value=idade_padrao[1],
            step=1.0,
            format="%.0f",
            key="f_idade",
            on_change=_guardar,
            args=("f_idade",),
        )
        st.button(
            "Limpar filtros",
            icon=":material/filter_alt_off:",
            on_click=_limpar_filtros,
            args=(idade_padrao,),
            width="stretch",
        )
        st.caption("Os filtros valem para todas as páginas do Spaceship Titanic. Nenhuma opção marcada = todas.")


def _valor(key: str, padrao):
    return st.session_state.get(key, st.session_state.get(f"_{key}", padrao))


def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    mascara = pd.Series(True, index=df.index)
    for key, (_, col) in FILTROS_PILLS.items():
        selecionados = _valor(key, ORDENS[col]) or ORDENS[col]
        if set(selecionados) != set(ORDENS[col]):
            mascara &= df[col].isin(selecionados)
    idade = _valor("f_idade", None)
    if idade is not None and "Age" in df.columns:
        mascara &= df["Age"].between(*idade) | df["Age"].isna()
    return df[mascara]


def descricao_filtros() -> str:
    partes = []
    for key, (titulo, col) in FILTROS_PILLS.items():
        sel = _valor(key, ORDENS[col]) or ORDENS[col]
        if set(sel) != set(ORDENS[col]):
            partes.append(f"{titulo}: " + ", ".join(formatar(col, v) for v in sel))
    idade = _valor("f_idade", None)
    completo = carregar()["Age"]
    if idade is not None and (idade[0] > completo.min() or idade[1] < completo.max()):
        partes.append(f"Idade: {idade[0]:.0f}–{idade[1]:.0f}")
    return " | ".join(partes) if partes else "Sem filtros"


# ----------------------------------------------------------------------------
# Notas analíticas (texto do grupo, em arquivos .md)
# ----------------------------------------------------------------------------
def ler_nota(chave: str) -> str | None:
    """Retorna o texto da nota, ou None se ainda estiver pendente."""
    caminho = NOTAS / f"{chave}.md"
    if not caminho.exists():
        return None
    texto = caminho.read_text(encoding="utf-8")
    if not texto.strip() or MARCA_PENDENTE in texto:
        return None
    return texto


def nota(chave: str) -> None:
    texto = ler_nota(chave)
    with st.container(border=True):
        st.markdown(":material/edit_note: **Nota analítica**")
        if texto is None:
            st.caption(f"Pendente — escrever em `src/parte_especifica/notas/{chave}.md`")
        else:
            st.markdown(texto)


# ----------------------------------------------------------------------------
# Relatório exportável
# ----------------------------------------------------------------------------
def botao_relatorio(fig: go.Figure, chave: str, nota_chave: str | None = None) -> None:
    if st.button("Adicionar ao relatório", key=f"rel_{chave}", icon=":material/note_add:", type="tertiary"):
        st.session_state.setdefault("relatorio", []).append(
            {
                "titulo": fig.layout.title.text or "Gráfico",
                "fig": fig.to_json(),
                "nota": ler_nota(nota_chave) if nota_chave else None,
                "filtros": descricao_filtros(),
            }
        )
        st.toast("Gráfico adicionado ao relatório", icon=":material/check:")


def gerar_html_relatorio(cabecalho_md: str | None, kpis: dict[str, str], itens: list[dict]) -> str:
    def md(texto: str) -> str:
        linhas = []
        for linha in texto.splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("<!--"):
                continue
            while "**" in linha:
                linha = linha.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
            linhas.append(f"<p>{linha}</p>")
        return "\n".join(linhas)

    partes = [
        "<!doctype html><html lang='pt-br'><head><meta charset='utf-8'>",
        "<title>Relatório — Spaceship Titanic</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#1f2328}"
        "table{border-collapse:collapse}td,th{border:1px solid #d0d7de;padding:.4rem .8rem}"
        ".nota{background:#f6f8fa;border-left:4px solid #1f6feb;padding:.6rem 1rem;margin:.5rem 0 2rem}"
        ".filtros{color:#57606a;font-size:.9rem}</style></head><body>",
        "<h1>Relatório — Spaceship Titanic</h1>",
        f"<p class='filtros'>Gerado em {datetime.now():%d/%m/%Y %H:%M}</p>",
    ]
    if cabecalho_md:
        partes.append(md(cabecalho_md))
    partes.append("<h2>Indicadores</h2><table>")
    partes += [f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in kpis.items()]
    partes.append("</table><h2>Gráficos</h2>")
    for i, item in enumerate(itens):
        fig = pio.from_json(item["fig"])
        partes.append(f"<h3>{item['titulo']}</h3><p class='filtros'>Filtros: {item['filtros']}</p>")
        partes.append(fig.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False))
        if item.get("nota"):
            partes.append(f"<div class='nota'>{md(item['nota'])}</div>")
    partes.append("</body></html>")
    return "\n".join(partes)


# ----------------------------------------------------------------------------
# Registro das visualizações oficiais do grupo (usado em graficos.py)
# ----------------------------------------------------------------------------
@dataclass
class Grafico:
    nota: str  # nome do arquivo em notas/ (sem .md)
    criar: Callable[[pd.DataFrame], go.Figure]
    usar_filtros: bool = True


# ----------------------------------------------------------------------------
# Construtores de gráficos (o grupo usa em graficos.py; o explorador livre também)
# ----------------------------------------------------------------------------
def _layout(fig: go.Figure, titulo: str) -> go.Figure:
    fig.update_layout(title=titulo, margin=dict(t=60, b=40), legend_title_text=None, separators=SEPARADORES)
    return fig


SEPARADORES = ",."  # números no padrão brasileiro nos gráficos: 50,4% e 5.915


def n_fmt(n: int) -> str:
    """Contagem com ponto de milhar (5915 -> 5.915)."""
    return f"{int(n):,}".replace(",", ".")


def _rotular_x(fig: go.Figure, df: pd.DataFrame, x: str) -> None:
    if x in FORMATO_OPCOES:
        valores = [str(v) for v in _ordem(df, x)]
        fig.update_xaxes(tickvals=valores, ticktext=[formatar(x, v) for v in valores])


def _ordem(df: pd.DataFrame, col: str) -> list:
    if col in ORDENS:
        return [v for v in ORDENS[col] if v in set(df[col])]
    return sorted(df[col].dropna().unique())


def histograma(df: pd.DataFrame, x: str, por_situacao: bool = True, percentual: bool = False,
               log_y: bool = False, titulo: str | None = None) -> go.Figure:
    fig = px.histogram(
        df, x=x,
        color="Situacao" if por_situacao else None,
        color_discrete_map=CORES_ALVO, color_discrete_sequence=[COR_DESTAQUE],
        category_orders={"Situacao": ORDENS["Situacao"]},
        barmode="overlay", opacity=0.75 if por_situacao else 1,
        histnorm="percent" if percentual else None,
        log_y=log_y, labels=ROTULOS,
    )
    fig.update_yaxes(title="% de passageiros" if percentual else "Nº de passageiros")
    return _layout(fig, titulo or f"Distribuição de {rotulo(x).lower()}")


def barras_contagem(df: pd.DataFrame, x: str, por_situacao: bool = True,
                    titulo: str | None = None) -> go.Figure:
    dados = df.assign(**{x: df[x].astype(str)})
    fig = px.histogram(
        dados, x=x,
        color="Situacao" if por_situacao else None,
        color_discrete_map=CORES_ALVO, color_discrete_sequence=[COR_DESTAQUE],
        category_orders={x: [str(v) for v in _ordem(df, x)], "Situacao": ORDENS["Situacao"]},
        barmode="group", labels=ROTULOS, text_auto=True,
    )
    fig.update_yaxes(title="Nº de passageiros")
    _rotular_x(fig, df, x)
    return _layout(fig, titulo or f"Passageiros por {rotulo(x).lower()}")


def taxa_transporte(df: pd.DataFrame, x: str, destacar: list | None = None,
                       titulo: str | None = None) -> go.Figure:
    """Barras com a taxa de transporte por categoria de `x`.

    `destacar`: categorias pintadas com a cor de destaque (as demais ficam neutras).
    """
    g = df.groupby(x, observed=True)["Transported"].agg(taxa="mean", n="size").reset_index()
    ordem = _ordem(df, x)
    g[x] = pd.Categorical(g[x], categories=ordem, ordered=True)
    g = g.sort_values(x)
    categorias = [str(v) for v in g[x]]
    if destacar:
        alvo = {str(v) for v in destacar}
        cores = [COR_DESTAQUE if c in alvo else COR_NEUTRA for c in categorias]
    else:
        cores = [COR_DESTAQUE] * len(categorias)
    fig = go.Figure(go.Bar(
        x=categorias, y=g["taxa"], marker_color=cores,
        text=[f"{t:.0%}<br>n={n_fmt(n)}" for t, n in zip(g["taxa"], g["n"])],
        # rótulo dentro da barra, no topo: não fica em cima da linha da média
        textposition="inside", insidetextanchor="end", textangle=0,
        textfont_color=["#ffffff" if c == COR_DESTAQUE else "#1f2328" for c in cores],
        hovertemplate="%{x}<br>Taxa: %{y:.1%}<extra></extra>",
    ))
    media = df["Transported"].mean()
    fig.add_hline(y=media, line_dash="dash", line_color="#57606a", layer="below",  # atrás das barras e rótulos
                  annotation_text=f"Média do<br>recorte: {media:.0%}", annotation_position="right",
                  annotation_font_color="#57606a")
    fig.update_xaxes(title=rotulo(x), type="category", tickvals=categorias,
                     ticktext=[formatar(x, c) for c in categorias])
    fig.update_yaxes(title="Taxa de transporte", tickformat=".0%", range=[0, 1.15])
    fig.update_layout(margin=dict(r=110))
    return _layout(fig, titulo or f"Taxa de transporte por {rotulo(x).lower()}")


def taxa_dois_fatores(df: pd.DataFrame, linhas: str, colunas: str, titulo: str | None = None) -> go.Figure:
    taxa = df.pivot_table(index=linhas, columns=colunas, values="Transported", aggfunc="mean", observed=True)
    n = df.pivot_table(index=linhas, columns=colunas, values="Transported", aggfunc="size", observed=True)
    taxa = taxa.reindex(index=_ordem(df, linhas), columns=_ordem(df, colunas))
    n = n.reindex_like(taxa)
    texto = [[("" if pd.isna(t) else f"{t:.0%}<br>n={n_fmt(c)}") for t, c in zip(lt, lc)]
             for lt, lc in zip(taxa.to_numpy(), n.to_numpy())]
    fig = go.Figure(go.Heatmap(
        z=taxa.to_numpy(), x=[str(c) for c in taxa.columns], y=[str(i) for i in taxa.index],
        text=texto, texttemplate="%{text}", colorscale="Blues", zmin=0, zmax=1,
        colorbar=dict(title="Taxa", tickformat=".0%"),
        hovertemplate=f"{rotulo(linhas)}: %{{y}}<br>{rotulo(colunas)}: %{{x}}<br>Taxa: %{{z:.1%}}<extra></extra>",
    ))
    xs, ys = [str(c) for c in taxa.columns], [str(i) for i in taxa.index]
    fig.update_xaxes(title=rotulo(colunas), type="category", tickvals=xs, ticktext=[formatar(colunas, v) for v in xs])
    fig.update_yaxes(title=rotulo(linhas), type="category", autorange="reversed",
                     tickvals=ys, ticktext=[formatar(linhas, v) for v in ys])
    return _layout(fig, titulo or f"Taxa de transporte por {rotulo(linhas).lower()} × {rotulo(colunas).lower()}")


def dispersao(df: pd.DataFrame, x: str, y: str, log_y: bool = False, titulo: str | None = None) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color="Situacao", color_discrete_map=CORES_ALVO,
        category_orders={"Situacao": ORDENS["Situacao"]},
        opacity=0.7, log_y=log_y, labels=ROTULOS, hover_data=["HomePlanet", "CryoSleep", "Destination"],
    )
    return _layout(fig, titulo or f"{rotulo(x)} × {rotulo(y)}")


def boxplot(df: pd.DataFrame, x: str, y: str, por_situacao: bool = True, log_y: bool = False,
            titulo: str | None = None) -> go.Figure:
    dados = df.assign(**{x: df[x].astype(str)})
    fig = px.box(
        dados, x=x, y=y,
        color="Situacao" if por_situacao else None,
        color_discrete_map=CORES_ALVO, color_discrete_sequence=[COR_DESTAQUE],
        category_orders={x: [str(v) for v in _ordem(df, x)], "Situacao": ORDENS["Situacao"]},
        log_y=log_y, labels=ROTULOS, points="outliers",
    )
    _rotular_x(fig, df, x)
    return _layout(fig, titulo or f"{rotulo(y)} por {rotulo(x).lower()}")


def taxa_ausencia(df: pd.DataFrame, por: str, variaveis: list[str], titulo: str | None = None) -> go.Figure:
    """Proporção de valores ausentes no dado original, por categoria de `por`."""
    colunas = {f"Falt_{v}": v for v in variaveis}
    g = df.groupby(por, observed=True)[list(colunas)].mean().rename(columns=colunas).reset_index()
    g = g.melt(id_vars=por, var_name="Variável", value_name="ausencia")
    g[por] = g[por].astype(str)
    fig = px.bar(
        g, x=por, y="ausencia", color="Variável", barmode="group",
        category_orders={por: [str(v) for v in _ordem(df, por)]},
        labels={**ROTULOS, "ausencia": "Proporção ausente"},
    )
    fig.update_yaxes(tickformat=".1%", rangemode="tozero")
    _rotular_x(fig, df, por)
    return _layout(fig, titulo or f"Proporção de valores ausentes por {rotulo(por).lower()}")
