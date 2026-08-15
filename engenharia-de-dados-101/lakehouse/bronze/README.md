# bronze/

## Objetivo

Ingerir os três arquivos de [`../landing/`](../landing/README.md) sem
limpar nada, apenas estruturando tudo em tabelas (CSV) e adicionando
rastreabilidade de onde/quando cada linha veio.

**Regra de ouro da bronze: não corrija, não filtre, não descarte.** Se um
valor está vazio ou errado na landing, ele continua vazio ou errado na
bronze. Duplicatas continuam duplicadas. A única coisa nova que a bronze
adiciona são as colunas de metadados `arquivo_origem` e `dt_ingestao`.

Por que fazer isso, se "não estamos limpando nada"? Porque a bronze serve
como um **backup fiel e consultável** da landing: se um mês depois você
descobrir que a lógica de limpeza da silver estava errada, você reprocessa
a partir da bronze, sem precisar voltar nos arquivos originais (que podem
já ter sido substituídos por uma nova exportação).

## O que fazer

1. Abra [`ingestao.py`](ingestao.py) e implemente as três funções
   marcadas com `TODO`:
   - `ler_vendas_csv()`
   - `ler_clientes_json()`
   - `ler_produtos_txt()`
2. Rode:
   ```bash
   python lakehouse/bronze/ingestao.py
   ```
3. Verifique seu trabalho:
   ```bash
   python lakehouse/bronze/verificar_bronze.py
   ```
4. Corrija o que o verificador apontar e rode de novo até aparecer
   "TUDO CERTO!".

## Saída esperada

Três arquivos em `saida/`:

- `vendas_bronze.csv`
- `clientes_bronze.csv`
- `produtos_bronze.csv`

Cada um com as colunas originais **mais** `arquivo_origem` e
`dt_ingestao`.

## Próximo passo

Com a bronze validada, siga para [`../silver/`](../silver/README.md).
