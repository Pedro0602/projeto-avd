# [IA] Claude – página explanatória (conteúdo e gráficos definidos pelo grupo)
import streamlit as st

from src.parte_especifica import dash_comum as dc
from src.parte_especifica import graficos

df = dc.carregar()
filtrado = dc.aplicar_filtros(df)

st.title("Explanatória", anchor=False)

texto = dc.ler_nota("storytelling")
if texto:
    st.markdown(texto)
else:
    st.info("Escrever o raciocínio do storytelling em `src/parte_especifica/notas/storytelling.md`.",
            title="Storytelling pendente", icon=":material/edit_note:")

if not graficos.EXPLANATORIAS:
    st.info("Registrar as 2 visualizações explanatórias em `src/parte_especifica/graficos.py` "
            "(lista `EXPLANATORIAS`).", title="Nenhuma visualização registrada", icon=":material/info:")

for i, g in enumerate(graficos.EXPLANATORIAS):
    base = filtrado if g.usar_filtros else df
    if base.empty:
        st.warning("Nenhum passageiro no recorte atual. Ajuste os filtros.")
        break
    fig = g.criar(base)
    with st.container(border=True):
        st.plotly_chart(fig, key=f"expl_{i}", alt=fig.layout.title.text)
        dc.botao_relatorio(fig, f"expl_{i}", g.nota)
    dc.nota(g.nota)
