# Projeto Final AVD — Agrupamento, EDA e Dashboard Interativo

Análise e Visualização de Dados (AVD) — 2026.2

| Parte | Dataset |
|---|---|
| Comum | [Obesity (UCI 544)](https://archive.ics.uci.edu/dataset/544) |
| Específica | [Spaceship Titanic (Kaggle)](https://www.kaggle.com/competitions/spaceship-titanic/data) |

## Integrantes

| Nome | GitHub |
|---|---|
| Pedro Henrique | [Pedro0602](https://github.com/Pedro0602) |
| Henrique | [HenriqueCBrito](https://github.com/HenriqueCBrito) |
| João Lucas | [JRobalinh0](https://github.com/JRobalinh0) |
| Tiago | [tiagooEM](https://github.com/tiagooEM) |

## Estrutura

```
projeto-avd/
├─ README.md
├─ requirements.txt
├─ CONTRIBUICAO.md            # matriz de contribuição
├─ data/
│  ├─ parte_comum/            # ObesityDataSet_raw_and_data_sinthetic.csv
│  └─ parte_especifica/       # CSVs do Spaceship Titanic
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

**Parte Específica (Spaceship Titanic):** o CSV fornecido pelo grupo deve ficar em
`data/parte_especifica/spaceship_train.csv` (8.693 passageiros, 14 colunas). Se o arquivo não estiver
disponível, baixe o ZIP da [competição Spaceship Titanic](https://www.kaggle.com/competitions/spaceship-titanic/data)
e extraia-o com:

```bash
python -m src.parte_especifica.preparar_dados caminho/para/spaceship-titanic.zip
```

O notebook `src/parte_especifica/eda.ipynb` gera `spaceship_tratado.csv`. Sem esse arquivo, o dashboard aplica
o tratamento padrão diretamente ao CSV original.

## Execução

```bash
# Parte Comum
jupyter notebook notebooks/parte_comum/eda.ipynb
jupyter notebook notebooks/parte_comum/kmeans_metricas.ipynb

# Parte Comum — alternativa por linha de comando
python -m src.parte_comum.kmeans --modo livre --out ./out/parte_comum/          # k pelo cotovelo
python -m src.parte_comum.kmeans --modo livre --k 4 --out ./out/parte_comum/    # k escolhido pelo grupo
python -m src.parte_comum.kmeans --modo fixo --out ./out/parte_comum/           # k = 7 classes
python -m src.parte_comum.kmeans --modo fixo --variaveis todas --out ./out/parte_comum/  # inclui as categóricas

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

## Rodar em outro computador (ex.: na apresentação)

O dashboard roda no computador, não fica publicado na internet.

1. Clone o repositório em uma pasta curta, como `C:\avd`. Pastas muito longas podem fazer o `pip` falhar no Windows.
2. Crie e ative o ambiente, depois instale as bibliotecas (precisa de internet):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Prepare o dataset com o ZIP do Kaggle (leve o ZIP num pendrive ou baixe no Kaggle):

```bash
python -m src.parte_especifica.preparar_dados caminho/para/spaceship-titanic.zip
```

4. Abra o dashboard. Ele aparece em http://localhost:8501:

```bash
streamlit run src/parte_especifica/dashboard.py
```

## Relatório

O script junta os textos escritos pelo grupo (notebooks e `src/parte_especifica/notas/`) e os gráficos. Ele não escreve análise. Precisa do Chrome ou do Edge.

```bash
# Rascunho em out/relatorio_rascunho.pdf, com as pendências em vermelho
python -m src.gerar_relatorio
```

```bash
# Versão final em relatorio.pdf (só gera se não houver pendências)
python -m src.gerar_relatorio --final
```

Nas células de análise, mantenham `Análise do grupo:` no início e apaguem `_(preencher)_`.

## Uso de IA

Trechos de código feitos com apoio de IA estão marcados com `# [IA] <ferramenta> – <finalidade>`.
