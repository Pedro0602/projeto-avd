# [IA] Claude – página de exploração: gráficos do grupo + explorador livre
import streamlit as st

from src.parte_especifica import dash_comum as dc
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

# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
elif modo == "Explorador livre":
    tipo = st.segmented_control(
        "Tipo de análise",
        ["Distribuição", "Relação entre duas variáveis", "Sobrevivência por grupo", "Dados faltantes", "Tabela"],
        default="Distribuição", key="exp_tipo",
    )
    todas = dc.NUMERICAS + dc.CATEGORICAS

    if tipo == "Distribuição":
        with st.container(horizontal=True, vertical_alignment="bottom"):
            var = st.selectbox("Variável", todas, format_func=dc.rotulo, key="dist_var")
            separar = st.toggle("Separar por sobrevivência", value=True, key="dist_sep")
            pct = st.toggle("Em %", value=False, key="dist_pct", disabled=var not in dc.NUMERICAS)
        if var in dc.NUMERICAS:
            fig = dc.histograma(filtrado, var, por_sobrevivencia=separar, percentual=pct)
        else:
            fig = dc.barras_contagem(filtrado, var, por_sobrevivencia=separar and var != "Sobrevivencia")

    elif tipo == "Relação entre duas variáveis":
        with st.container(horizontal=True, vertical_alignment="bottom"):
            x = st.selectbox("Eixo X", todas, index=todas.index("Pclass"), format_func=dc.rotulo, key="rel_x")
            y = st.selectbox("Eixo Y", todas, index=todas.index("Fare"), format_func=dc.rotulo, key="rel_y")
            log = st.toggle("Escala log no eixo Y", value=False, key="rel_log")
        num_x, num_y = x in dc.NUMERICAS, y in dc.NUMERICAS
        if x == y:
            st.warning("Escolha duas variáveis diferentes.")
            st.stop()
        if num_x and num_y:
            fig = dc.dispersao(filtrado, x, y, log_y=log)
        elif num_x or num_y:
            cat, num = (y, x) if num_x else (x, y)
            fig = dc.boxplot(filtrado, cat, num, por_sobrevivencia=cat != "Sobrevivencia", log_y=log)
        else:
            fig = dc.taxa_dois_fatores(filtrado, y, x)
        st.caption("Numérica × numérica: dispersão · categórica × numérica: boxplot · "
                   "categórica × categórica: taxa de sobrevivência em cada combinação.")

    elif tipo == "Sobrevivência por grupo":
        opcoes = [c for c in dc.CATEGORICAS if c != "Sobrevivencia"] + ["FamilySize", "SibSp", "Parch"]
        with st.container(horizontal=True, vertical_alignment="bottom"):
            var = st.selectbox("Agrupar por", opcoes, format_func=dc.rotulo, key="surv_var")
            segunda = st.selectbox("Cruzar com (opcional)", [None] + opcoes, key="surv_var2",
                                   format_func=lambda c: "—" if c is None else dc.rotulo(c))
        if segunda and segunda != var:
            fig = dc.taxa_dois_fatores(filtrado, var, segunda)
        else:
            categorias = [str(v) for v in dc._ordem(filtrado, var)]
            destacar = st.pills("Destacar categorias", categorias, selection_mode="multi", key=f"surv_dest_{var}",
                                format_func=lambda v: dc.formatar(var, v))
            fig = dc.taxa_sobrevivencia(filtrado, var, destacar=destacar or None)

    elif tipo == "Dados faltantes":
        bruto = dc.aplicar_filtros(dc.carregar_bruto())
        por = st.selectbox("Comparar ausência por", ["Pclass", "Sex", "Sobrevivencia", "Embarked", "Title"],
                           format_func=dc.rotulo, key="falt_por")
        fig = dc.taxa_ausencia(bruto, por)
        st.caption("Calculado sobre o dado original (antes da imputação).")

    else:  # Tabela
        colunas = ["PassengerId", "Name", "Sobrevivencia", "Pclass", "Sex", "Age", "Age_missing", "SibSp",
                   "Parch", "FamilySize", "Fare", "Embarked", "Title", "Deck", "Ticket", "TicketGroupSize"]
        st.dataframe(
            filtrado[colunas], hide_index=True, alt="Passageiros do recorte atual",
            column_config={c: st.column_config.Column(dc.rotulo(c)) for c in colunas}
            | {"Fare": st.column_config.NumberColumn(dc.rotulo("Fare"), format="%.2f")},
        )
        st.download_button("Baixar CSV do recorte", filtrado[colunas].to_csv(index=False).encode("utf-8"),
                            file_name="titanic_recorte.csv", mime="text/csv", icon=":material/download:")
        st.stop()

    with st.container(border=True):
        st.plotly_chart(fig, key="explorador", alt=fig.layout.title.text)
        dc.botao_relatorio(fig, "explorador")
