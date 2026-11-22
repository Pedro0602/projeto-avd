# [IA] Claude – página de visão geral
import streamlit as st

from src.parte_especifica import dash_comum as dc

df = dc.carregar()
filtrado = dc.aplicar_filtros(df)

st.title("Spaceship Titanic", anchor=False)
st.caption(f"{len(df):,} passageiros".replace(",", ".") + f" · recorte atual: {dc.descricao_filtros()}")

texto = dc.ler_nota("visao_geral")
if texto:
    st.markdown(texto)
else:
    st.info("Escrever a pergunta de pesquisa e o público-alvo em `src/parte_especifica/notas/visao_geral.md`.",
            title="Pergunta de pesquisa pendente", icon=":material/edit_note:")

if filtrado.empty:
    st.warning("Nenhum passageiro no recorte atual. Ajuste os filtros.")
    st.stop()

taxa_geral = df["Transported"].mean()
taxa = filtrado["Transported"].mean()
with st.container(horizontal=True):
    st.metric("Passageiros", f"{len(filtrado):,}".replace(",", "."), border=True)
    st.metric("Taxa de transporte", f"{taxa:.0%}", delta=f"{(taxa - taxa_geral) * 100:+.0f} p.p. vs. total",
              delta_color="off", border=True)
    st.metric("Idade mediana", f"{filtrado['Age'].median():.0f} anos", border=True)
    st.metric("Gasto total mediano", f"{filtrado['TotalSpend'].median():.0f}", border=True)
    st.metric("Com algum faltante", f"{(filtrado['N_faltantes'] > 0).mean():.0%}", border=True,
              help="Passageiros com ao menos um valor ausente no dado original.")

with st.container(border=True):
    st.markdown(":material/dataset: **Sobre os dados**")
    st.markdown(
        "- Fonte: [Spaceship Titanic (Kaggle)](https://www.kaggle.com/competitions/spaceship-titanic/data), "
        "licença CC BY 4.0\n"
        "- 8.693 linhas e 14 colunas originais, mais variáveis derivadas de grupo, cabine, gastos e idade\n"
        "- Tratamento de faltantes descrito em `src/parte_especifica/eda.ipynb` (nenhuma linha removida)"
    )
