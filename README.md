# TP1 ISI - Recomendador de filmes (ETL)

Trabalho Prático I de Integração de Sistemas de Informação (2026/27), IPCA.
Autor: Alexandre Barbosa (31539)

## Descrição
Processo ETL em Pentaho Data Integration (Kettle) que integra dados de filmes
do IMDb (TSV) com uma lista de filmes vistos (XML) e carrega o resultado numa
base de dados MySQL.

## Conteúdo
- `A_Filmes.ktr` - transformação A: filmes, ratings e géneros
- `B_Vistos.ktr` - transformação B: limpeza do vistos.xml
- `Job_Principal.kjb` - job que corre A e B por ordem
- `preparar_dados.py` - filtra os dados do IMDb e gera o vistos.xml com erros propositados
- `dados/` - ficheiros de entrada e de rejeitados

## Como executar
1. Descarregar title.basics.tsv.gz e title.ratings.tsv.gz de datasets.imdbws.com para `dados/`
2. `python preparar_dados.py`
3. Criar a base de dados `filmes_db` no MySQL
4. Abrir o `Job_Principal.kjb` no Spoon (PDI 10.2, Java 11) e executar
