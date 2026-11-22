# [IA] Claude – página de exploração: gráficos do grupo + explorador livre
import streamlit as st

from src.parte_especifica import dash_comum as dc
from src.parte_especifica import dados as dd
from src.parte_especifica import graficos

df = dc.carregar()
filtrado = dc.aplicar_filtros(df)

st.title("Exploração", anchor=False)
st.caption(f"{len(filtrado)} passageiros · {dc.descricao_filtros()}")

if filtrado.empty:
    st.warning("Nenhum passageiro no recorte atual. Ajuste os filtros.")
    st.stop()

modo = st.segmented_control(
    "Seção", ["Visualizações do grupo", "Explorador livre"], default="Visualizações do grupo",
    key="exp_modo", label_visibility="collapsed",
)

if modo == "Visualizações do grupo":
    if not graficos.EXPLORATORIAS:
        st.info("Registrar as 4 visualizações exploratórias em `src/parte_especifica/graficos.py` "
                "(lista `EXPLORATORIAS`). Enquanto isso, use o explorador livre.",
                title="Nenhuma visualização registrada", icon=":material/info:")
    for i, g in enumerate(graficos.EXPLORATORIAS):
        fig = g.criar(filtrado if g.usar_filtros else df)
        with st.container(border=True):
            st.plotly_chart(fig, key=f"exp_oficial_{i}", alt=fig.layout.title.text)
            dc.botao_relatorio(fig, f"exp_oficial_{i}", g.nota)
        dc.nota(g.nota)

elif modo == "Explorador livre":
    tipo = st.segmented_control(
        "Tipo de análise",
        ["Distribuição", "Relação entre duas variáveis", "Transporte por grupo", "Dados faltantes", "Tabela"],
        default="Distribuição", key="exp_tipo",
    )
    todas = dc.NUMERICAS + dc.CATEGORICAS
    fig = None

    if tipo == "Distribuição":
        with st.container(horizontal=True, vertical_alignment="bottom"):
            var = st.selectbox("Variável", todas, format_func=dc.rotulo, key="dist_var")
            separar = st.toggle("Separar por situação", value=True, key="dist_sep")
            pct = st.toggle("Em %", value=False, key="dist_pct", disabled=var not in dc.NUMERICAS)
            log = st.toggle("Eixo Y em log", value=False, key="dist_log", disabled=var not in dc.NUMERICAS)
        if var in dc.NUMERICAS:
            fig = dc.histograma(filtrado, var, por_situacao=separar, percentual=pct, log_y=log)
        else:
            fig = dc.barras_contagem(filtrado, var, por_situacao=separar and var != "Situacao")

    elif tipo == "Relação entre duas variáveis":
        with st.container(horizontal=True, vertical_alignment="bottom"):
            x = st.selectbox("Eixo X", todas, index=todas.index("HomePlanet"), format_func=dc.rotulo, key="rel_x")
            y = st.selectbox("Eixo Y", todas, index=todas.index("Age"), format_func=dc.rotulo, key="rel_y")
            log = st.toggle("Escala log no eixo Y", value=False, key="rel_log")
        if x == y:
            st.warning("Escolha duas variáveis diferentes.")
            st.stop()
        num_x, num_y = x in dc.NUMERICAS, y in dc.NUMERICAS
        if num_x and num_y:
            fig = dc.dispersao(filtrado, x, y, log_y=log)
        elif num_x or num_y:
            cat, num = (y, x) if num_x else (x, y)
            fig = dc.boxplot(filtrado, cat, num, por_situacao=cat != "Situacao", log_y=log)
        elif "Situacao" in (x, y):
            outra = y if x == "Situacao" else x
            fig = dc.barras_contagem(filtrado, outra, por_situacao=True)
        else:
            fig = dc.taxa_dois_fatores(filtrado, y, x)
        st.caption("Numérica × numérica: dispersão · categórica × numérica: boxplot · "
                   "categórica × categórica: taxa de transporte em cada combinação. "
                   "Na escala log, valores iguais a zero não aparecem.")

    elif tipo == "Transporte por grupo":
        opcoes = [c for c in dc.CATEGORICAS if c != "Situacao"] + ["GroupSize"]
        with st.container(horizontal=True, vertical_alignment="bottom"):
            var = st.selectbox("Agrupar por", opcoes, format_func=dc.rotulo, key="alvo_var")
            segunda = st.selectbox("Cruzar com (opcional)", [None] + opcoes, key="alvo_var2",
                                   format_func=lambda c: "—" if c is None else dc.rotulo(c))
        if segunda and segunda != var:
            fig = dc.taxa_dois_fatores(filtrado, var, segunda)
        else:
            categorias = [str(v) for v in dc._ordem(filtrado, var)]
            destacar = st.pills("Destacar categorias", categorias, selection_mode="multi", key=f"alvo_dest_{var}",
                                format_func=lambda v: dc.formatar(var, v))
            fig = dc.taxa_transporte(filtrado, var, destacar=destacar or None)

    elif tipo == "Dados faltantes":
        with st.container(horizontal=True, vertical_alignment="bottom"):
            por = st.selectbox("Comparar ausência por",
                               ["Situacao", "HomePlanet", "CryoSleep", "Destination", "VIP", "Deck", "AgeGroup"],
                               format_func=dc.rotulo, key="falt_por")
            variaveis = st.multiselect("Variáveis", dd.COLUNAS_COM_FALTANTES,
                                       default=["Age", "CryoSleep", "Cabin", "VIP"], key="falt_vars")
        if not variaveis:
            st.warning("Escolha ao menos uma variável.")
            st.stop()
        fig = dc.taxa_ausencia(filtrado, por, variaveis)
        st.caption("Ausência no dado original, antes do tratamento.")

    elif tipo == "Tabela":
        resumo = (
            filtrado.groupby(["HomePlanet", "CryoSleep", "Destination"], observed=True)
            .agg(passageiros=("Transported", "size"), taxa=("Transported", "mean"),
                 idade=("Age", "median"), gasto=("TotalSpend", "median"))
            .reset_index()
        )
        st.dataframe(
            resumo, hide_index=True, alt="Resumo dos passageiros por planeta, sono criogênico e destino",
            column_config={
                "HomePlanet": dc.rotulo("HomePlanet"), "CryoSleep": dc.rotulo("CryoSleep"),
                "Destination": dc.rotulo("Destination"), "passageiros": "Passageiros",
                "taxa": st.column_config.ProgressColumn("Taxa de transporte", min_value=0, max_value=1, format="percent"),
                "idade": st.column_config.NumberColumn("Idade mediana", format="%.0f"),
                "gasto": st.column_config.NumberColumn("Gasto total mediano", format="%.0f"),
            },
        )
        st.download_button("Baixar resumo em CSV", resumo.to_csv(index=False).encode("utf-8"),
                           file_name="spaceship_resumo.csv", mime="text/csv", icon=":material/download:")

    if fig is not None:
        with st.container(border=True):
            st.plotly_chart(fig, key="explorador", alt=fig.layout.title.text)
            dc.botao_relatorio(fig, "explorador")
