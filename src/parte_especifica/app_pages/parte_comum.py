# [IA] Claude – página da Parte Comum: cotovelo, transição animada entre passadas, matrizes e métricas
import pandas as pd
import streamlit as st

from src.parte_comum import kmeans as km
from src.parte_especifica import dash_kmeans as dk

st.title("Parte comum — K-Means sobre Obesity", anchor=False)
st.caption("2111 pessoas · 8 variáveis numéricas padronizadas (z-score) · 7 classes reais de NObeyesdad")

df, X, proj, var, curva = dk.preparar()
k_sugerido = km.sugerir_k_cotovelo(curva)
K_FIXO = df[km.ALVO].nunique()

k_livre = st.slider("k da Passada 1 (livre)", 2, 10, value=k_sugerido, key="k_livre",
                    help=f"Sugestão automática pelo cotovelo: k = {k_sugerido}. A escolha final é do grupo.")

secao = st.segmented_control(
    "Seção", ["Cotovelo", "Transição entre passadas", "Matrizes e métricas"],
    default="Cotovelo", key="pc_secao", label_visibility="collapsed",
)

if secao == "Cotovelo":
    st.plotly_chart(dk.fig_cotovelo(curva, k_livre, k_sugerido), key="cotovelo",
                    alt="Curva de inércia do K-Means para k de 2 a 10")
    tabela = curva.assign(queda=-curva["inercia"].pct_change())
    st.dataframe(
        tabela, hide_index=True, alt="Inércia por k",
        column_config={
            "k": "k",
            "inercia": st.column_config.NumberColumn("Inércia", format="%.0f"),
            "queda": st.column_config.NumberColumn("Queda em relação ao k anterior", format="percent"),
        },
    )

elif secao == "Transição entre passadas":
    sequencia_nome = st.segmented_control(
        "Sequência",
        [f"Passada 1 (k={k_livre}) → Passada 2 (k={K_FIXO}) → classes reais", "k = 2 → 10 → classes reais"],
        default=f"Passada 1 (k={k_livre}) → Passada 2 (k={K_FIXO}) → classes reais", key="pc_seq",
    )
    if sequencia_nome and sequencia_nome.startswith("k ="):
        sequencia = [*dk.KS, "real"]
    else:
        sequencia = [k_livre, K_FIXO, "real"]
    st.plotly_chart(dk.fig_transicao(sequencia), key="transicao",
                    alt="Animação dos agrupamentos do K-Means projetados em PCA")
    st.caption("Cada ponto é uma pessoa, na mesma posição em todas as etapas (projeção PCA). "
               "A cor é a classe majoritária do cluster em que a pessoa caiu; na última etapa, a classe real.")

else:
    res_livre, res_fixo = dk.passada(k_livre), dk.passada(K_FIXO)
    colunas = st.columns(2)
    for col, res, nome in [(colunas[0], res_livre, f"Passada 1 — k livre = {k_livre}"),
                           (colunas[1], res_fixo, f"Passada 2 — k fixo = {K_FIXO}")]:
        with col, st.container(border=True):
            st.subheader(nome, anchor=False)
            st.metric("Acurácia (cluster mapeado × classe real)", f"{res['acuracia']:.1%}")
            st.plotly_chart(dk.fig_matriz(res["matriz"], "Matriz de confusão"), key=f"mat_{nome}",
                            alt=f"Matriz de confusão da {nome}")
            st.dataframe(
                res["por_classe"].reset_index(), hide_index=True, alt=f"Precisão e recall por classe — {nome}",
                column_config={
                    "real": "Classe",
                    "precisao": st.column_config.ProgressColumn("Precisão", min_value=0, max_value=1, format="percent"),
                    "recall": st.column_config.ProgressColumn("Recall", min_value=0, max_value=1, format="percent"),
                    "suporte": "Pessoas",
                },
            )
            st.caption("Precisão vazia = nenhum cluster foi mapeado para essa classe.")
            st.markdown("**Mapeamento cluster → classe**")
            st.dataframe(pd.Series(res["mapa"], name="Classe majoritária").rename_axis("Cluster").reset_index(),
                         hide_index=True, alt=f"Mapeamento de clusters — {nome}")
            st.plotly_chart(dk.fig_contingencia(res["contingencia"], "Classes reais dentro de cada cluster"),
                            key=f"cont_{nome}", alt=f"Tabela de contingência da {nome}")
