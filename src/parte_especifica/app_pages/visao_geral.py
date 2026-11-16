# [IA] Claude – página de visão geral
import streamlit as st

from src.parte_especifica import dash_comum as dc

df = dc.carregar()
filtrado = dc.aplicar_filtros(df)

st.title("Titanic", anchor=False)
st.caption(f"891 passageiros do Titanic · recorte atual: {dc.descricao_filtros()}")

texto = dc.ler_nota("visao_geral")
if texto:
    st.markdown(texto)
else:
    st.info("Escrever a pergunta de pesquisa e o público-alvo em `src/parte_especifica/notas/visao_geral.md`.",
            title="Pergunta de pesquisa pendente", icon=":material/edit_note:")

if filtrado.empty:
    st.warning("Nenhum passageiro no recorte atual. Ajuste os filtros.")
    st.stop()

taxa_geral = df["Survived"].mean()
taxa = filtrado["Survived"].mean()
with st.container(horizontal=True):
    st.metric("Passageiros", f"{len(filtrado)}", border=True)
    st.metric("Taxa de sobrevivência", f"{taxa:.0%}", delta=f"{(taxa - taxa_geral) * 100:+.0f} p.p. vs. total",
              delta_color="off" if len(filtrado) == len(df) else "normal", border=True)
    st.metric("Idade mediana", f"{filtrado['Age'].median():.0f} anos", border=True)
    st.metric("Tarifa mediana", f"{filtrado['Fare'].median():.2f}", border=True)
    st.metric("Idades imputadas", f"{(filtrado['Age_missing'] == 'Sim').mean():.0%}", border=True,
              help="Passageiros sem idade no dado original, preenchida no tratamento.")

with st.container(border=True):
    st.markdown(":material/dataset: **Sobre os dados**")
    st.markdown(
        "- Fonte: [DT Titanic Dataset (Kaggle)](https://www.kaggle.com/datasets/qurat01/dt-titanic-dataset)\n"
        "- 891 linhas, 12 colunas originais + 6 derivadas (pronome de tratamento, tamanho da família, deck, "
        "cabine registrada, idade ausente, passageiros no mesmo bilhete)\n"
        "- Tratamento de faltantes descrito em `src/parte_especifica/eda.ipynb` (nenhuma linha removida)"
    )
