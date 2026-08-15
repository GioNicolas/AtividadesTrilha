# Guia do Aluno

Bem-vindo(a)! Este guia te leva, passo a passo, por todo o exercício.
Siga a ordem — cada camada depende do resultado da anterior.

## 0. Preparação

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Confirme que está tudo certo rodando:

```bash
python --version   # precisa ser 3.10+
```

## 1. Entenda o cenário

Você trabalha na "Loja Boa Compra". O time de dados recebe, todo dia,
três arquivos de sistemas diferentes:

- `lakehouse/landing/vendas.csv` — exportação do sistema de vendas.
- `lakehouse/landing/clientes.json` — exportação do cadastro de clientes.
- `lakehouse/landing/produtos.txt` — exportação do catálogo de produtos
  (um sistema legado que só exporta texto delimitado por `|`).

Sua missão: construir um pipeline que transforma esses arquivos brutos
(e cheios de problemas) em métricas de negócio confiáveis, e depois um
relatório visual para o time comercial.

Antes de escrever qualquer código, **abra os três arquivos** em
`lakehouse/landing/` com um editor de texto. Gaste 5 minutos só olhando:
que problemas você já consegue enxergar de olho nu?

## 2. Camada Bronze — ingestão crua

📂 Pasta: [`lakehouse/bronze/`](../lakehouse/bronze/README.md)

**O que fazer:** ler os três arquivos da landing e salvá-los como CSV,
sem limpar nada, só adicionando de onde e quando cada linha veio.

```bash
# 1. Implemente as funções TODO em:
#    lakehouse/bronze/ingestao.py

# 2. Rode a ingestão:
python lakehouse/bronze/ingestao.py

# 3. Verifique:
python lakehouse/bronze/verificar_bronze.py
```

Só avance quando aparecer `TUDO CERTO!`.

## 3. Camada Silver — limpeza e padronização

📂 Pasta: [`lakehouse/silver/`](../lakehouse/silver/README.md)

**O que fazer:** aplicar as regras de limpeza descritas no README da
silver (tipos corretos, sem duplicatas, formatos padronizados,
integridade referencial).

```bash
# 1. Implemente as funções TODO em:
#    lakehouse/silver/transformacao.py

# 2. Rode a transformação:
python lakehouse/silver/transformacao.py

# 3. Verifique:
python lakehouse/silver/verificar_silver.py
```

Dica: leia o README da silver com atenção — as regras de negócio (o que
descartar, como padronizar cada campo) estão todas lá. O trabalho aqui é
transformar aquelas regras em código, não adivinhar as regras.

## 4. Camada Gold — métricas de negócio

📂 Pasta: [`lakehouse/gold/`](../lakehouse/gold/README.md)

**O que fazer:** agregar a silver em métricas prontas para consumo
(vendas por categoria, por mês, ranking de clientes, resumo geral).

```bash
# 1. Implemente as funções TODO em:
#    lakehouse/gold/agregacao.py

# 2. Rode a agregação:
python lakehouse/gold/agregacao.py

# 3. Verifique:
python lakehouse/gold/verificar_gold.py
```

## 5. Application — ETL reverso + Streamlit

📂 Pasta: [`application/`](../application/README.md)

**O que fazer:** carregar os 4 CSVs que você gerou na gold para dentro de
um banco SQLite (`application/database.sqlite`), sem mudar nada de
estrutura — é uma ingestão simples, não tem agregação nem SQL
sofisticado aqui (isso já foi feito na gold). Esse padrão de "levar dado
já agregado de volta para um banco relacional" se chama **ETL reverso**.
Depois, um app Streamlit já pronto lê esse banco e monta o relatório.

```bash
# 1. Implemente as funções TODO em:
#    application/etl_reverso.py

# 2. Rode a carga:
python application/etl_reverso.py

# 3. Verifique:
python application/verificar_etl_reverso.py

# 4. Veja o relatório de verdade:
streamlit run application/app.py
```

Isso abre uma aba do navegador com KPIs, gráficos e tabelas.

## 6. Checklist final

- [ ] `python lakehouse/bronze/verificar_bronze.py` → TUDO CERTO!
- [ ] `python lakehouse/silver/verificar_silver.py` → TUDO CERTO!
- [ ] `python lakehouse/gold/verificar_gold.py` → TUDO CERTO!
- [ ] `python application/verificar_etl_reverso.py` → TUDO CERTO!
- [ ] `streamlit run application/app.py` abre e mostra o relatório sem
      erros.

## Dúvidas comuns

**"Meu verificador falhou, e agora?"**
Leia a mensagem `[FALHOU]` com calma — ela diz exatamente qual coluna,
arquivo ou regra está errada, e geralmente mostra um exemplo do valor
problemático. Corrija só aquilo e rode de novo.

**"Posso mudar os scripts `verificar_*.py`?"**
Não precisa, e não é recomendado — eles são o "gabarito" do exercício.
Se um deles parecer errado, fale com o instrutor.

**"Meu resultado tem um número de linhas diferente do de um colega, isso
é problema?"**
Na bronze e no ETL reverso (`application/`), não deveria acontecer — são
cópias fiéis. Na silver e na gold, uma pequena diferença é normal — o que
importa é que as regras do README sejam seguidas e o verificador passe.

**"Posso usar pandas?"**
Não neste projeto — o objetivo é praticar Python puro e biblioteca
padrão. A única exceção é o Streamlit no exercício final.
