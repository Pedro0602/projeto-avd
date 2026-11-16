# Projeto Final AVD — Agrupamento, EDA e Dashboard Interativo

Análise e Visualização de Dados (AVD) — 2026.2

| Parte | Dataset |
|---|---|
| Comum | [Obesity (UCI 544)](https://archive.ics.uci.edu/dataset/544) |
| Específica | [Titanic (Kaggle)](https://www.kaggle.com/datasets/qurat01/dt-titanic-dataset) |

## Integrantes

| Nome | GitHub |
|---|---|
|  |  |
|  |  |
|  |  |
|  |  |

## Estrutura

```
projeto-avd/
├─ README.md
├─ requirements.txt
├─ CONTRIBUICAO.md            # matriz de contribuição
├─ data/
│  ├─ parte_comum/            # ObesityDataSet_raw_and_data_sinthetic.csv
│  └─ parte_especifica/       # Titanic
├─ out/
│  ├─ parte_comum/
│  └─ parte_especifica/
├─ notebooks/
│  └─ parte_comum/
│     ├─ eda.ipynb
│     └─ kmeans_metricas.ipynb
├─ src/
│  ├─ parte_comum/
│  │  └─ baixar_dados.py      # download do dataset Obesity
│  └─ parte_especifica/
│     ├─ eda.ipynb
│     └─ dashboard.py         # app Streamlit
└─ relatorio.pdf
```

## Instalação

Requer Python 3.11+.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Dados

**Parte Comum (Obesity):**

```bash
python -m src.parte_comum.baixar_dados
```

O CSV é salvo em `data/parte_comum/`.

**Parte Específica (Titanic):** baixar o CSV pelo link do Kaggle acima (exige login) e salvar em `data/parte_especifica/`.

## Execução

```bash
# Parte Comum
jupyter notebook notebooks/parte_comum/eda.ipynb
jupyter notebook notebooks/parte_comum/kmeans_metricas.ipynb

# Parte Específica
jupyter notebook src/parte_especifica/eda.ipynb
streamlit run src/parte_especifica/dashboard.py
```

## Uso de IA

Trechos de código feitos com apoio de IA estão marcados com `# [IA] <ferramenta> – <finalidade>`.
