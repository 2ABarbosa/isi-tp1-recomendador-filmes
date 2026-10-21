#!/usr/bin/env python3
"""
Prepara os dados para o TP1 de ISI (recomendador de filmes).

Faz:
  1. Descarrega title.basics e title.ratings do IMDb (datasets.imdbws.com)
  2. Filtra filmes (titleType = movie), ano >= ANO_MIN e votos >= VOTOS_MIN
  3. Grava os TSV filtrados em ./dados/ (mais pequenos e fáceis de ler no Pentaho)
  4. Gera ./dados/vistos.xml com filmes "vistos" e erros propositados
     (maiúsculas/minúsculas trocadas, espaços a mais, datas em formatos
     diferentes, duplicados) para teres o que limpar com regex.

Só usa a biblioteca padrão do Python 3. Precisa de ligação à internet.
Uso:  python preparar_dados.py
"""
import csv
import gzip
import os
import random
import shutil
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

BASE_URL = "https://datasets.imdbws.com/"
FICHEIROS = ["title.basics.tsv.gz", "title.ratings.tsv.gz"]
PASTA = "dados"
ANO_MIN = 2000
VOTOS_MIN = 20000
N_VISTOS = 40
random.seed(42)  # resultados repetíveis


def descarregar(nome):
    destino = os.path.join(PASTA, nome)
    if os.path.exists(destino):
        print(f"[ok] {nome} já existe")
        return destino
    print(f"[..] a descarregar {nome} ...")
    req = urllib.request.Request(BASE_URL + nome, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r, open(destino, "wb") as f:
        shutil.copyfileobj(r, f)
    return destino


def ler_tsv_gz(caminho):
    with gzip.open(caminho, "rt", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def main():
    os.makedirs(PASTA, exist_ok=True)
    basics_gz = descarregar(FICHEIROS[0])
    ratings_gz = descarregar(FICHEIROS[1])

    # 1) ratings com votos suficientes
    ratings = {}
    for row in ler_tsv_gz(ratings_gz):
        try:
            votos = int(row["numVotes"])
        except ValueError:
            continue
        if votos >= VOTOS_MIN:
            ratings[row["tconst"]] = row

    # 2) filmes filtrados (mantém "\\N" para nulos: é um caso real a tratar no ETL)
    filmes = []
    for row in ler_tsv_gz(basics_gz):
        if row["titleType"] != "movie" or row["tconst"] not in ratings:
            continue
        ano = row["startYear"]
        if ano == "\\N" or not ano.isdigit() or int(ano) < ANO_MIN:
            continue
        filmes.append(row)

    campos_b = ["tconst", "titleType", "primaryTitle", "originalTitle",
                "isAdult", "startYear", "endYear", "runtimeMinutes", "genres"]
    with open(os.path.join(PASTA, "title.basics.filtrado.tsv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos_b, delimiter="\t",
                           quoting=csv.QUOTE_NONE, escapechar="\\",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(filmes)

    ids = {f["tconst"] for f in filmes}
    campos_r = ["tconst", "averageRating", "numVotes"]
    with open(os.path.join(PASTA, "title.ratings.filtrado.tsv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos_r, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(r for t, r in ratings.items() if t in ids)

    print(f"[ok] {len(filmes)} filmes guardados em {PASTA}/")

    # 3) vistos.xml com erros propositados
    escolhidos = random.sample(filmes, min(N_VISTOS, len(filmes)))
    raiz = ET.Element("vistos")

    def estragar_titulo(t):
        modo = random.choice(["ok", "ok", "lower", "upper", "espacos", "ponto"])
        if modo == "lower":
            return t.lower()
        if modo == "upper":
            return t.upper()
        if modo == "espacos":
            return "  " + t.replace(" ", "   ", 1) + " "
        if modo == "ponto":
            return t + "."
        return t

    def data_aleatoria():
        d = date(2024, 1, 1) + timedelta(days=random.randint(0, 650))
        fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%y", "%b %d, %Y"])
        return d.strftime(fmt)

    entradas = []
    for f in escolhidos:
        entradas.append((estragar_titulo(f["primaryTitle"]), f["startYear"]))
    # duplicados propositados
    entradas += random.sample(entradas, 3)
    random.shuffle(entradas)

    for titulo, ano in entradas:
        el = ET.SubElement(raiz, "filme")
        ET.SubElement(el, "titulo").text = titulo
        # alguns sem ano (nulos propositados)
        ET.SubElement(el, "ano").text = "" if random.random() < 0.1 else ano
        nota = random.choice([str(random.randint(1, 10)), str(random.randint(1, 10)),
                              f"{random.randint(1, 10)},5", "abc"])
        ET.SubElement(el, "nota").text = nota
        ET.SubElement(el, "data_visto").text = data_aleatoria()

    ET.indent(raiz)
    ET.ElementTree(raiz).write(os.path.join(PASTA, "vistos.xml"),
                               encoding="utf-8", xml_declaration=True)
    print(f"[ok] vistos.xml com {len(entradas)} entradas (com erros propositados)")


if __name__ == "__main__":
    main()
