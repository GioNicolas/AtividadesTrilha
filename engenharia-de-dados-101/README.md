# Fiz até a SILVER completa, faltou a gold

# Engenharia de Dados 101

Você vai construir, do zero, um pipeline com **arquitetura medalhão**
(landing → bronze → silver → gold) usando **apenas Python puro e a
biblioteca padrão** (sem pandas!) e terminar fechando o ciclo com um
**ETL reverso** (gold → banco de dados) e um pequeno relatório em
**Streamlit**.

> 📘 **Primeira vez aqui?** Vá direto para o
> [Guia do Aluno](docs/GUIA_DO_ALUNO.md) — ele te leva passo a passo por
> todo o exercício, na ordem certa.

## O que você vai praticar

- Ler dados "sujos" em três formatos diferentes: CSV, JSON e um TXT com
  formato customizado.
- Aplicar os 4 estágios clássicos de uma arquitetura medalhão:
  **landing → bronze → silver → gold**.
- Escrever suas próprias validações de qualidade de dados (tipos,
  duplicatas, integridade referencial).
- Fazer um **ETL reverso** com `sqlite3`: carregar métricas já prontas de
  volta para um banco relacional.
- Montar um relatório com Streamlit.

Tudo isso sem pandas: só `csv`, `json`, `sqlite3`, `re`, `pathlib`,
`datetime` e `collections` — as ferramentas que já vêm com o Python.

## Arquitetura do projeto

```
┌──────────┐  1. ler+estruturar  ┌──────────┐  2. limpar+padronizar  ┌──────────┐  3. agregar  ┌──────────┐  4. ETL reverso   ┌──────────────────┐
│ landing/ │ ──────────────────▶ │ bronze/  │ ─────────────────────▶│ silver/  │ ────────────▶│  gold/   │ ─────────────────▶ │ application/       │
│.csv .json│                     │  (cru,   │                        │ (limpo,  │              │(métricas │  (sem mudar        │ database.sqlite    │
│   .txt   │                     │rastreável)│                       │confiável)│              │ negócio) │   estrutura)        │ streamlit run 📊   │
└──────────┘                     └──────────┘                        └──────────┘              └──────────┘                     └──────────────────┘
```

Todas as camadas do lakehouse (landing/bronze/silver/gold) ficam dentro
da pasta [`lakehouse/`](lakehouse/). O último passo (`application/`) lê
os CSVs que você mesmo gerou na gold e os carrega, sem nenhuma
transformação, em `application/database.sqlite` — um banco que só passa
a existir depois que você roda esse exercício (não vem pronto no
repositório). O app Streamlit então lê só desse banco, que é o único
banco de dados do projeto.

## Estrutura de pastas

```
engenharia-de-dados-101/
├── lakehouse/
│   ├── landing/                # arquivos brutos, com problemas propositais
│   │   ├── vendas.csv
│   │   ├── clientes.json
│   │   └── produtos.txt
│   ├── bronze/                 # EXERCÍCIO 1: ingestão crua + rastreabilidade
│   │   ├── ingestao.py         #   <- você edita
│   │   ├── verificar_bronze.py
│   │   └── saida/
│   ├── silver/                 # EXERCÍCIO 2: limpeza e padronização
│   │   ├── transformacao.py    #   <- você edita
│   │   ├── verificar_silver.py
│   │   └── saida/
│   └── gold/                   # EXERCÍCIO 3: métricas de negócio
│       ├── agregacao.py        #   <- você edita
│       ├── verificar_gold.py
│       └── saida/
│
├── application/                # EXERCÍCIO 4: ETL reverso (gold -> banco) + Streamlit
│   ├── etl_reverso.py          #   <- você edita
│   ├── verificar_etl_reverso.py
│   ├── app.py
│   ├── database.sqlite         # gerado por você ao rodar etl_reverso.py (não vem pronto)
│   └── dev_cli.py              # (dev) CLI: criar / popular / limpar database.sqlite
│
├── docs/
│   └── GUIA_DO_ALUNO.md        # passo a passo completo
│
└── requirements.txt
```

## Pré-requisitos

- Python 3.10 ou mais recente.
- Nenhuma outra dependência para os exercícios de `lakehouse/` (só
  biblioteca padrão).
- Para o exercício final (`application/`): Streamlit.

## Como começar

1. (Opcional, mas recomendado) crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Windows: .venv\Scripts\activate
   ```
2. Instale a única dependência externa do projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Siga o [Guia do Aluno](docs/GUIA_DO_ALUNO.md) — ele indica a ordem
   exata: `lakehouse/bronze` → `lakehouse/silver` → `lakehouse/gold` →
   `application/`.

Cada camada tem seu próprio `README.md` com as regras do exercício, e um
script `verificar_*.py` que você roda para conferir se o seu resultado
está correto — sem depender de ninguém olhar seu código.

## Filosofia do exercício

- **Você só edita arquivos com `TODO` dentro de funções.** Tudo o mais
  (leitura de configuração, escrita de CSV, o app Streamlit) já está
  pronto, para você focar na lógica de dados.
- **Os scripts `verificar_*.py` são o seu feedback imediato.** Rode
  sempre que terminar uma função — eles apontam exatamente o que está
  faltando ou errado, em português.
- **Não existe uma única "resposta certa" para tudo.** Bronze e o ETL
  reverso (`application/`) exigem cópia fiel — os valores têm que bater
  exatamente com a entrada. Silver e gold verificam **regras e
  consistência**, não números fixos — pequenas variações de implementação
  são esperadas e aceitas, desde que sigam as regras do README de cada
  camada.
