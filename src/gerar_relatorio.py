# [IA] Claude – monta o relatório em PDF juntando os textos escritos pelo grupo e os gráficos do projeto
"""Gera o relatório do projeto. Este script não escreve análise: só organiza o que o grupo escreveu.

Rascunho (mostra em vermelho o que falta):
    python -m src.gerar_relatorio

Versão final (só gera relatorio.pdf se não houver nenhuma pendência):
    python -m src.gerar_relatorio --final

Precisa do Google Chrome ou do Microsoft Edge instalado para criar o PDF.
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import mistune

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

NOTAS = RAIZ / "src" / "parte_especifica" / "notas"
RASCUNHO = RAIZ / "out" / "relatorio_rascunho.pdf"
FINAL = RAIZ / "relatorio.pdf"

# (título, notebook, pasta dos gráficos, nº de células de análise esperadas)
NOTEBOOKS = {
    "eda_comum": ("EDA do Obesity", RAIZ / "notebooks/parte_comum/eda.ipynb", RAIZ / "out/parte_comum/eda", 4),
    "kmeans": ("K-Means e métricas", RAIZ / "notebooks/parte_comum/kmeans_metricas.ipynb", RAIZ / "out/parte_comum", 6),
    "eda_especifica": ("EDA do Spaceship Titanic", RAIZ / "src/parte_especifica/eda.ipynb",
                       RAIZ / "out/parte_especifica/eda", 6),
}

MARCA_ANALISE = "Análise do grupo"
MD = mistune.create_markdown(plugins=["table", "strikethrough"], escape=True)

CSS = """
@page { size: A4; margin: 18mm 17mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #1f2328; }
h1 { font-size: 21pt; margin: 0 0 12pt; break-before: page; border-bottom: 2px solid #1f6feb; padding-bottom: 4pt; }
h2 { font-size: 15pt; margin: 18pt 0 6pt; break-after: avoid; }
h3 { font-size: 12.5pt; margin: 14pt 0 4pt; break-after: avoid; }
h4 { font-size: 11pt; margin: 10pt 0 3pt; break-after: avoid; color: #57606a; }
p { margin: 0 0 7pt; text-align: justify; }
figure { margin: 8pt 0 12pt; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 215mm; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 6pt 0 10pt; break-inside: avoid; }
td, th { border: 1px solid #d0d7de; padding: 3pt 6pt; text-align: left; }
th { background: #f0f3f6; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: #f0f3f6; padding: 0 2pt; }
.capa { height: 235mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.capa h1 { break-before: auto; border: 0; font-size: 28pt; }
.capa p { text-align: center; }
.pendente { border: 1.5px solid #d1242f; background: #ffebe9; color: #a40e26; padding: 5pt 8pt; margin: 6pt 0 10pt;
            font-weight: 600; font-size: 10pt; break-inside: avoid; }
.aviso { border: 1.5px solid #d1242f; color: #a40e26; padding: 6pt; text-align: center; font-weight: 700; }
.grafico { break-inside: avoid; margin: 8pt 0; }
.nota { border-left: 3px solid #1f6feb; background: #f6f8fa; padding: 6pt 10pt; margin-bottom: 14pt; }
.sumario li { margin-bottom: 2pt; }
"""


class Relatorio:
    def __init__(self) -> None:
        self.partes: list[str] = []
        self.pendencias: list[str] = []

    def add(self, conteudo: str) -> None:
        self.partes.append(conteudo)

    def pendente(self, descricao: str) -> None:
        self.pendencias.append(descricao)
        self.add(f'<div class="pendente">PENDENTE: {html.escape(descricao)}</div>')

    def titulo(self, nivel: int, texto: str) -> None:
        self.add(f"<h{nivel}>{html.escape(texto)}</h{nivel}>")

    def nota(self, nome: str, descricao: str) -> None:
        texto = ler_nota(nome)
        if texto is None:
            self.pendente(f"{descricao} (src/parte_especifica/notas/{nome}.md)")
        else:
            self.add(MD(texto))


def ler_nota(nome: str) -> str | None:
    caminho = NOTAS / f"{nome}.md"
    if not caminho.exists():
        return None
    texto = caminho.read_text(encoding="utf-8")
    return None if not texto.strip() or "PENDENTE" in texto else texto


def limpar_analise(fonte: str) -> str:
    """Tira a marcação do modelo e as perguntas-guia (linhas inteiras em itálico)."""
    if "(preencher)" in fonte:
        return ""
    texto = re.sub(r"^\s*>?\s*(?:✍️)?\s*(?:\*\*)?Análise do grupo:(?:\*\*)?\s*", "", fonte, count=1)
    linhas = [l for l in texto.splitlines() if not re.fullmatch(r"\s*(?:-\s*)?_[^_]+_\s*", l)]
    return "\n".join(linhas).strip()


def adicionar_notebook(rel: Relatorio, chave: str) -> None:
    nome, caminho, pasta, esperadas = NOTEBOOKS[chave]
    celulas = json.loads(caminho.read_text(encoding="utf-8"))["cells"]
    titulos: list[tuple[int, str]] = []  # só entram no PDF quando a seção tem conteúdo
    usados: set[str] = set()
    encontradas = 0

    def descarregar() -> None:
        for nivel, texto in titulos:
            rel.titulo(nivel, texto)
        titulos.clear()

    for celula in celulas:
        fonte = "".join(celula["source"])
        if celula["cell_type"] == "code":
            for arquivo in re.findall(r'"([\w-]+\.png)"', fonte):
                imagem = pasta / arquivo
                if arquivo not in usados and imagem.exists():
                    usados.add(arquivo)
                    descarregar()
                    rel.add(f'<figure><img src="{imagem.as_uri()}" alt="{html.escape(arquivo)}"></figure>')
            continue
        cabecalho = re.match(r"(#{2,3})\s+(.+)", fonte)
        if cabecalho:
            nivel = len(cabecalho.group(1)) + 1
            while titulos and titulos[-1][0] >= nivel:
                titulos.pop()
            titulos.append((nivel, cabecalho.group(2).split("\n")[0].replace("`", "")))
        if MARCA_ANALISE in fonte:
            encontradas += 1
            descarregar()
            texto = limpar_analise(fonte)
            if texto:
                rel.add(MD(texto))
            else:
                rel.pendente(f"análise {encontradas} de {esperadas} em {caminho.relative_to(RAIZ).as_posix()}")

    if encontradas != esperadas:
        rel.pendente(f"{caminho.name}: esperadas {esperadas} células '{MARCA_ANALISE}', encontradas {encontradas}. "
                     f"Mantenha '{MARCA_ANALISE}:' no início de cada célula.")


def adicionar_graficos(rel: Relatorio, lista: list, prefixo: str, esperados: int, tipo: str, df) -> None:
    for g in lista:
        fig = g.criar(df)
        fig.update_layout(width=650, height=400, template="plotly_white")  # cabe na largura útil do A4
        incluir_js = not getattr(rel, "plotly_incluido", False)
        rel.plotly_incluido = True
        rel.add('<div class="grafico">' + fig.to_html(full_html=False, include_plotlyjs=incluir_js,
                                                      config={"staticPlot": True}) + "</div>")
        texto = ler_nota(g.nota)
        if texto is None:
            rel.pendente(f"nota analítica {g.nota}.md")
        else:
            rel.add(f'<div class="nota">{MD(texto)}</div>')
    for i in range(len(lista), esperados):
        rel.pendente(f"gráfico {tipo} {prefixo}_{i + 1} em src/parte_especifica/graficos.py")


def integrantes() -> list[str]:
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    trecho = readme.split("## Integrantes", 1)[-1].split("\n## ", 1)[0]
    nomes = [l.split("|")[1].strip() for l in trecho.splitlines() if l.startswith("|")]
    return [n for n in nomes if n and n != "Nome" and not set(n) <= {"-"}]


def montar() -> tuple[str, list[str]]:
    logging.disable(logging.WARNING)  # o cache do Streamlit avisa quando roda fora do app
    from src.parte_especifica import dados as dd
    from src.parte_especifica import dash_comum as dc
    from src.parte_especifica import graficos

    rel = Relatorio()
    rel.add('<div class="capa"><h1>Projeto Final — Agrupamento, EDA e Dashboard Interativo</h1>'
            "<p>Análise e Visualização de Dados (AVD) — 2026.2</p><br>"
            + "".join(f"<p><strong>{html.escape(n)}</strong></p>" for n in integrantes())
            + f"<br><p>{date.today():%d/%m/%Y}</p></div>")
    rel.add('<!--AVISO--><h1>Sumário</h1><ol class="sumario"><li>Introdução</li><li>Parte Comum: Obesity</li>'
            "<li>Parte Específica: Spaceship Titanic</li><li>Conclusão</li><li>Matriz de contribuição</li></ol>")

    rel.titulo(1, "1. Introdução")
    rel.nota("introducao", "introdução")

    rel.titulo(1, "2. Parte Comum: Obesity")
    rel.titulo(2, "2.1 Análise exploratória")
    adicionar_notebook(rel, "eda_comum")
    rel.titulo(2, "2.2 K-Means, métricas e discussão crítica")
    adicionar_notebook(rel, "kmeans")

    rel.titulo(1, "3. Parte Específica: Spaceship Titanic")
    rel.titulo(2, "3.1 Pergunta de pesquisa e público-alvo")
    rel.nota("visao_geral", "pergunta de pesquisa e público-alvo")
    rel.titulo(2, "3.2 Análise exploratória")
    adicionar_notebook(rel, "eda_especifica")
    rel.titulo(2, "3.3 Storytelling")
    rel.nota("storytelling", "storytelling")

    if dd.CAMINHO_BRUTO.exists():
        df = dc.carregar()
        rel.titulo(2, "3.4 Visualizações exploratórias")
        adicionar_graficos(rel, graficos.EXPLORATORIAS, "exp", 4, "exploratório", df)
        rel.titulo(2, "3.5 Visualizações explanatórias")
        adicionar_graficos(rel, graficos.EXPLANATORIAS, "expl", 2, "explanatório", df)
    else:
        rel.pendente("dataset ausente: rode python -m src.parte_especifica.preparar_dados <ZIP do Kaggle>")

    rel.titulo(1, "4. Conclusão")
    rel.nota("conclusao", "resposta à pergunta de pesquisa e conclusão")

    rel.titulo(1, "5. Matriz de contribuição")
    matriz = (RAIZ / "CONTRIBUICAO.md").read_text(encoding="utf-8").split("\n", 1)[1]
    rel.add(MD(matriz))

    corpo = "\n".join(rel.partes)
    if rel.pendencias:
        aviso = f'<div class="aviso">RASCUNHO: {len(rel.pendencias)} pendência(s)</div>'
        corpo = corpo.replace("<!--AVISO--><h1>Sumário</h1>", f"<h1>Sumário</h1>{aviso}", 1)
    pagina = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório AVD</title>'
              f"<style>{CSS}</style></head><body>{corpo}</body></html>")
    return pagina, rel.pendencias


def achar_navegador() -> str:
    candidatos = [
        os.environ.get("CHROME"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser"),
        shutil.which("microsoft-edge"),
    ]
    for caminho in candidatos:
        if caminho and Path(caminho).exists():
            return caminho
    raise SystemExit("Chrome ou Edge não encontrado. Instale um deles ou defina a variável CHROME.")


def gerar_pdf(pagina: str, destino: Path) -> None:
    navegador = achar_navegador()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        arquivo = Path(tmp) / "relatorio.html"
        arquivo.write_text(pagina, encoding="utf-8")
        temporario = Path(tmp) / "relatorio.pdf"
        subprocess.run(
            [navegador, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
             "--no-pdf-header-footer", f"--user-data-dir={Path(tmp) / 'perfil'}", "--virtual-time-budget=30000",
             f"--print-to-pdf={temporario}", arquivo.as_uri()],
            check=False, timeout=240, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if not temporario.exists() or temporario.stat().st_size == 0:
            raise SystemExit("O navegador não conseguiu criar o PDF.")
        shutil.copyfile(temporario, destino)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o relatório em PDF")
    parser.add_argument("--final", action="store_true", help="gera relatorio.pdf; recusa se houver pendências")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    pagina, pendencias = montar()
    if pendencias:
        print(f"{len(pendencias)} pendência(s):")
        for item in pendencias:
            print(f"  - {item}")
    if args.final and pendencias:
        raise SystemExit("\nrelatorio.pdf NÃO foi gerado: resolva as pendências acima.")

    destino = FINAL if args.final else RASCUNHO
    gerar_pdf(pagina, destino)
    print(f"\nPDF gerado: {destino} ({destino.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
