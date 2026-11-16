# [IA] Claude – app Streamlit: navegação entre páginas e filtros globais
"""Dashboard do Projeto AVD.

Executar a partir da raiz do repositório:
    streamlit run src/parte_especifica/dashboard.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from src.parte_especifica import dash_comum as dc  # noqa: E402

st.set_page_config(page_title="Projeto AVD — Titanic", page_icon=":material/sailing:", layout="wide")

st.session_state.setdefault("relatorio", [])

PAGINAS_TITANIC = [
    st.Page("app_pages/visao_geral.py", title="Visão geral", icon=":material/home:", default=True,
            help="Pergunta de pesquisa, público-alvo e indicadores do recorte filtrado."),
    st.Page("app_pages/exploracao.py", title="Exploração", icon=":material/query_stats:",
            help="Visualizações exploratórias do grupo e um explorador livre de variáveis."),
    st.Page("app_pages/comparacao.py", title="Comparação", icon=":material/compare_arrows:",
            help="Dois grupos de passageiros lado a lado, cada um com seus próprios filtros."),
    st.Page("app_pages/explanatoria.py", title="Explanatória", icon=":material/campaign:",
            help="A história dos dados: as visualizações explanatórias e as notas do grupo."),
    st.Page("app_pages/relatorio.py", title="Relatório", icon=":material/description:",
            help="Gráficos adicionados ao relatório e exportação em HTML."),
]
PAGINAS_COMUM = [
    st.Page("app_pages/parte_comum.py", title="K-Means (Obesity)", icon=":material/scatter_plot:",
            help="Parte Comum: cotovelo, transição animada entre as passadas, matrizes e métricas."),
]

pagina = st.navigation({"Titanic": PAGINAS_TITANIC, "Parte comum": PAGINAS_COMUM})

if pagina in PAGINAS_TITANIC:
    dc.filtros_sidebar(dc.carregar())
    n = len(st.session_state["relatorio"])
    st.sidebar.caption(f":material/description: {n} gráfico(s) no relatório")

pagina.run()
