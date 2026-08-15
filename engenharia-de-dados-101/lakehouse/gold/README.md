# gold/

## Objetivo

Transformar a silver (limpa) em métricas de negócio prontas para consumo:
totais por categoria, evolução mensal, ranking de clientes. É o tipo de
dado que alguém da área comercial olharia direto num dashboard.

## O que produzir

| Arquivo                        | Colunas                                          | Descrição                                              |
|----------------------------------|---------------------------------------------------|----------------------------------------------------------|
| `resumo_vendas_categoria.csv`   | `categoria, quantidade_vendida, valor_total`      | Uma linha por categoria de produto                        |
| `vendas_por_mes.csv`            | `mes, quantidade_vendas, valor_total`             | Uma linha por mês (`AAAA-MM`)                              |
| `top_clientes.csv`              | `id_cliente, nome, valor_total`                   | Os 10 clientes que mais gastaram, do maior para o menor    |
| `resumo_geral.csv`              | `total_vendas, valor_total_geral, ticket_medio`   | Uma única linha com os totais gerais                       |

## O que fazer

1. Rode a silver primeiro, se ainda não rodou.
2. Abra [`agregacao.py`](agregacao.py) e implemente:
   - `calcular_resumo_por_categoria()`
   - `calcular_vendas_por_mes()`
   - `calcular_top_clientes()`
   - `calcular_resumo_geral()`
3. Rode:
   ```bash
   python lakehouse/gold/agregacao.py
   ```
4. Verifique:
   ```bash
   python lakehouse/gold/verificar_gold.py
   ```

## Como o verificador confere seu trabalho

Ele não compara com números "mágicos" fixos — ele recalcula os totais
direto de `silver/saida/vendas_silver.csv` (a sua própria silver) e
confere se os números batem com os seus arquivos gold. Ou seja: o
verificador está checando se a gold é **consistente** com a silver que
você mesmo produziu.

## Próximo passo

Depois que a gold estiver validada, siga para
[`../../application/`](../../application/README.md) — o último passo,
onde esses CSVs são carregados num banco de dados para o relatório em
Streamlit.
