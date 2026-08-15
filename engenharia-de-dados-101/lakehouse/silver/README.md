# silver/

## Objetivo

Transformar a bronze (crua) em dados **confiáveis**: tipados
corretamente, sem duplicatas, sem valores impossíveis, com categorias e
formatos padronizados. É aqui que a maior parte do trabalho de limpeza
acontece.

## Regras de negócio

Estas regras já são dadas — sua tarefa é implementá-las em código, não
inventá-las. Elas também estão documentadas como comentário no topo de
[`transformacao.py`](transformacao.py).

### `clientes_silver.csv`
- `id_cliente` vira inteiro.
- `email`: remove espaços, converte para minúsculo. Se não tiver `@`, o
  registro é **descartado** (e-mail impossível de corrigir).
- `estado`: remove espaços, converte para MAIÚSCULO (sigla de 2 letras).
- Se houver `id_cliente` duplicado, mantenha o **último** registro que
  aparece no arquivo (é o mais recente).

### `produtos_silver.csv`
- `id_produto` vira inteiro; `preco` vira `float` (troque `,` por `.`
  antes de converter).
- `categoria`: normalize para bater EXATAMENTE com uma das categorias
  oficiais: `Eletrônicos`, `Livros`, `Roupas`, `Alimentos`, `Brinquedos`.
- `ativo`: `"sim"` ou `"1"` → `1`; `"nao"`, `"não"`, `"0"` ou vazio → `0`.
- Se houver `id_produto` duplicado, mantenha a **primeira** ocorrência.

### `vendas_silver.csv`
- `id_venda`, `id_cliente`, `id_produto` viram inteiros.
- `data_venda`: aceita `"AAAA-MM-DD"` ou `"DD/MM/AAAA"` (às vezes com
  espaços em volta) → padronize sempre para `"AAAA-MM-DD"`.
- `quantidade`: vira inteiro. Linhas com quantidade vazia, zero ou
  negativa são **descartadas**.
- `valor_total`: vira `float` (troque `,` por `.`). Linhas com valor
  vazio são **descartadas**.
- Linhas **exatamente duplicadas** (mesmo `id_venda` repetido) → mantenha
  só uma ocorrência.
- Linhas cujo `id_cliente` ou `id_produto` não existir em
  `clientes_silver` / `produtos_silver` → **descartadas** (integridade
  referencial).

## O que fazer

1. Rode a bronze primeiro, se ainda não rodou.
2. Abra [`transformacao.py`](transformacao.py) e implemente:
   - `limpar_clientes()`
   - `limpar_produtos()`
   - `limpar_vendas()`
3. Rode:
   ```bash
   python lakehouse/silver/transformacao.py
   ```
4. Verifique:
   ```bash
   python lakehouse/silver/verificar_silver.py
   ```

## Por que o verificador não exige um número exato de linhas?

Diferente da bronze, aqui não existe uma única resposta "certa" de quantas
linhas devem sobreviver à limpeza — depende de pequenas decisões de
implementação. O que o verificador confere é se o RESULTADO é consistente
com as regras acima (sem duplicatas, sem valores inválidos, integridade
referencial preservada).

## Próximo passo

Com a silver validada, siga para [`../gold/`](../gold/README.md).
