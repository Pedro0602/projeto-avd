# [IA] Claude – página de comparação lado a lado entre dois grupos de passageiros
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.parte_especifica import dash_comum as dc

df = dc.carregar()

st.title("Comparação", anchor=False)
st.caption("Dois grupos definidos de forma independente (os filtros da barra lateral não se aplicam aqui).")


def seletor_grupo(prefixo: str, planeta: list[str]) -> pd.DataFrame:
    with st.container(border=True):
        st.subheader(f"Grupo {prefixo}", anchor=False)
        mascara = pd.Series(True, index=df.index)
        for col, titulo in [("HomePlanet", "Planeta"), ("CryoSleep", "Sono criogênico"),
                            ("Destination", "Destino"), ("VIP", "VIP")]:
            padrao = planeta if col == "HomePlanet" else dc.ORDENS[col]
            sel = st.pills(titulo, dc.ORDENS[col], selection_mode="multi", default=padrao,
                           key=f"cmp_{prefixo}_{col}", format_func=lambda v, c=col: dc.formatar(c, v))
            if sel:
                mascara &= df[col].isin(sel)
        idade = st.slider("Idade", 0.0, 79.0, (0.0, 79.0), step=1.0, format="%.0f", key=f"cmp_{prefixo}_idade")
        mascara &= df["Age"].between(*idade)
        grupo = df[mascara]
        st.metric("Passageiros", len(grupo))
        if not grupo.empty:
            st.metric("Taxa de transporte", f"{grupo['Transported'].mean():.0%}")
            st.metric("Idade mediana", f"{grupo['Age'].median():.0f} anos")
            st.metric("Gasto total mediano", f"{grupo['TotalSpend'].median():.0f}")
        return grupo


col_a, col_b = st.columns(2)
with col_a:
    grupo_a = seletor_grupo("A", ["Earth"])
with col_b:
    grupo_b = seletor_grupo("B", ["Mars"])

if grupo_a.empty or grupo_b.empty:
    st.warning("Um dos grupos está vazio. Ajuste os filtros.")
    st.stop()

var = st.selectbox("Comparar a taxa de transporte por",
                   ["CryoSleep", "Destination", "VIP", "Deck", "Side", "AgeGroup", "Solo", "AnySpend"],
                   format_func=dc.rotulo, key="cmp_var")

fig = go.Figure()
for nome, grupo, cor in [("Grupo A", grupo_a, "#1f6feb"), ("Grupo B", grupo_b, "#bf8700")]:
    g = grupo.groupby(var, observed=True)["Transported"].agg(taxa="mean", n="size").reset_index()
    g[var] = g[var].astype(str)
    fig.add_trace(go.Bar(x=g[var], y=g["taxa"], name=nome, marker_color=cor,
                         text=[f"{t:.0%}<br>n={n}" for t, n in zip(g["taxa"], g["n"])], textposition="outside"))
fig.update_layout(title=f"Taxa de transporte por {dc.rotulo(var).lower()} — Grupo A × Grupo B",
                  barmode="group", legend_title_text=None)
ordem = [str(v) for v in dc._ordem(df, var)]
fig.update_xaxes(title=dc.rotulo(var), type="category", categoryorder="array", categoryarray=ordem,
                 tickvals=ordem, ticktext=[dc.formatar(var, v) for v in ordem])
fig.update_yaxes(title="Taxa de transporte", tickformat=".0%", range=[0, 1.15])

with st.container(border=True):
    st.plotly_chart(fig, key="cmp_fig", alt=fig.layout.title.text)
    dc.botao_relatorio(fig, "cmp_fig")
