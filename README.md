# Projeto Final AVD — Agrupamento, EDA e Dashboard Interativo

Análise e Visualização de Dados (AVD) — 2026.2

| Parte | Dataset |
|---|---|
| Comum | [Obesity (UCI 544)](https://archive.ics.uci.edu/dataset/544) |
| Específica | [Spaceship Titanic (Kaggle)](https://www.kaggle.com/competitions/spaceship-titanic/data), licença CC BY 4.0 |

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
│  └─ parte_especifica/       # Spaceship Titanic (script de preparação)
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

**Parte Específica (Spaceship Titanic):** as regras da competição não permitem redistribuir os dados, por isso o CSV não fica no repositório.

1. Entre em https://www.kaggle.com/competitions/spaceship-titanic/data e aceite as regras
2. Baixe o ZIP (Download All)
3. Rode:

```bash
python -m src.parte_especifica.preparar_dados caminho/para/spaceship-titanic.zip
```

O notebook `src/parte_especifica/eda.ipynb` gera `spaceship_tratado.csv` (dataset tratado). Sem esse arquivo, o dashboard aplica o tratamento padrão.

## Execução

```bash
# Parte Comum
jupyter notebook notebooks/parte_comum/eda.ipynb
jupyter notebook notebooks/parte_comum/kmeans_metricas.ipynb

# Parte Comum — alternativa por linha de comando
python -m src.parte_comum.kmeans --modo livre --out ./out/parte_comum/          # k pelo cotovelo
python -m src.parte_comum.kmeans --modo livre --k 4 --out ./out/parte_comum/    # k escolhido pelo grupo
python -m src.parte_comum.kmeans --modo fixo --out ./out/parte_comum/           # k = 7 classes

# Parte Específica
jupyter notebook src/parte_especifica/eda.ipynb
streamlit run src/parte_especifica/dashboard.py
```

## Dashboard

```bash
streamlit run src/parte_especifica/dashboard.py
```

| Página | Conteúdo |
|---|---|
| Visão geral | Pergunta de pesquisa, público-alvo e indicadores do recorte filtrado |
| Exploração | Visualizações exploratórias do grupo + explorador livre (escolha de variáveis e eixos) |
| Comparação | Dois grupos de passageiros lado a lado |
| Explanatória | Storytelling e visualizações explanatórias |
| Relatório | Gráficos adicionados pelo usuário, exportação em HTML |
| K-Means (Obesity) | Parte Comum: cotovelo, animação de transição entre as passadas, matrizes e métricas |

Os filtros da barra lateral (planeta, sono criogênico, destino, VIP, idade) valem para todas as páginas do Spaceship Titanic.

**Onde o grupo edita o conteúdo:**
- `src/parte_especifica/graficos.py` — registro das 4 visualizações exploratórias e das 2 explanatórias
- `src/parte_especifica/notas/*.md` — notas analíticas, pergunta de pesquisa, público-alvo e storytelling
  (apagar a linha `<!-- PENDENTE ... -->` ao preencher)

## Uso de IA

Trechos de código feitos com apoio de IA estão marcados com `# [IA] <ferramenta> – <finalidade>`.
