# [IA] Claude – página de montagem e exportação do relatório
import plotly.io as pio
import streamlit as st

from src.parte_especifica import dash_comum as dc
from src.parte_especifica import graficos

df = dc.carregar()
filtrado = dc.aplicar_filtros(df)
itens: list[dict] = st.session_state["relatorio"]

st.title("Relatório", anchor=False)
st.caption("Use “Adicionar ao relatório” abaixo de qualquer gráfico. O HTML exportado mantém os gráficos interativos.")


def adicionar_oficiais() -> None:
    for g in graficos.EXPLORATORIAS + graficos.EXPLANATORIAS:
        fig = g.criar(filtrado if g.usar_filtros else df)
        itens.append({"titulo": fig.layout.title.text or "Gráfico", "fig": fig.to_json(),
                      "nota": dc.ler_nota(g.nota), "filtros": dc.descricao_filtros()})


with st.container(horizontal=True):
    st.button("Adicionar as visualizações do grupo", icon=":material/playlist_add:", on_click=adicionar_oficiais,
              disabled=not (graficos.EXPLORATORIAS or graficos.EXPLANATORIAS))
    st.button("Esvaziar relatório", icon=":material/delete_sweep:", on_click=itens.clear, disabled=not itens)

if not itens:
    st.info("O relatório está vazio.", icon=":material/description:")
    st.stop()

kpis = {
    "Recorte": dc.descricao_filtros(),
    "Passageiros": str(len(filtrado)),
    "Taxa de sobrevivência": f"{filtrado['Survived'].mean():.0%}" if len(filtrado) else "—",
}
html = dc.gerar_html_relatorio(dc.ler_nota("visao_geral"), kpis, itens)
st.download_button("Baixar relatório (HTML)", html.encode("utf-8"), file_name="relatorio_titanic.html",
                   mime="text/html", icon=":material/download:", type="primary")

for i, item in enumerate(itens):
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"**{i + 1}. {item['titulo']}**  \n:gray[{item['filtros']}]")
            st.button("Remover", key=f"rm_{i}", icon=":material/close:", type="tertiary",
                      on_click=itens.pop, args=(i,))
        fig = pio.from_json(item["fig"])
        st.plotly_chart(fig, key=f"rel_fig_{i}", alt=item["titulo"])
        if item.get("nota"):
            st.markdown(item["nota"])
