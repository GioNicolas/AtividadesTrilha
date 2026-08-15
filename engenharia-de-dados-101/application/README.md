# application/

## Objetivo

Este é o último exercício: fechar o pipeline carregando o resultado da
camada [`gold`](../lakehouse/gold/README.md) em um banco de dados, para
um app Streamlit ler e montar um relatório visual.

O exercício em si (`etl_reverso.py`) é uma **ingestão simples**: pegar os
4 CSVs de `lakehouse/gold/saida/` e copiá-los, sem mudar nada de
estrutura, para tabelas de mesmo nome dentro de `application/database.sqlite`.
Não tem agregação nem limpeza aqui — isso já foi feito na gold. É só
"virar banco".

### Por que "ETL reverso"?

Num pipeline normal, dados fluem de sistemas operacionais para um banco
analítico — foi o que você fez em `landing → bronze → silver → gold`.
Aqui a gente inverte o sentido: pega o dado já analítico/agregado da gold
e carrega de volta num banco relacional simples. No mercado, esse padrão
é chamado de **reverse ETL** (reverter métricas prontas de um data
warehouse/lake de volta para um sistema operacional ou uma ferramenta que
consome dados via banco relacional — no nosso caso, o app Streamlit).

## Sobre o banco `database.sqlite`

Diferente das outras camadas, este banco **não vem pronto** — é você
quem cria, rodando `etl_reverso.py`. Ele não existe no repositório antes
disso (por isso está no `.gitignore`). É o único banco de dados do
projeto.

## Arquivos

| Arquivo                        | Você edita? | Descrição                                                        |
|-----------------------------------|:-----------:|---------------------------------------------------------------------|
| `etl_reverso.py`                  | **sim**      | Funções com `TODO` — carrega os CSVs da gold em `database.sqlite`    |
| `app.py`                          | não          | App Streamlit completo, lê `database.sqlite` e monta o relatório     |
| `verificar_etl_reverso.py`        | não          | Confere se a carga em `database.sqlite` está correta                 |
| `database.sqlite`                 | *(gerado)*   | Criado por você ao rodar `etl_reverso.py` — não existe até lá        |
| `dev_cli.py`                      | não          | *(fora do exercício)* CLI com comandos `criar`/`popular`/`limpar` para `database.sqlite` |

## O que fazer

1. Rode a gold primeiro, se ainda não rodou (precisa dos 4 CSVs em
   `lakehouse/gold/saida/`).

2. Abra [`etl_reverso.py`](etl_reverso.py) e implemente as 2 funções
   marcadas com `TODO`:
   - `criar_tabela()` — cria a tabela no banco com as colunas certas.
   - `inserir_linhas()` — insere as linhas do CSV, sem alterar valores.

3. Rode a carga:
   ```bash
   python application/etl_reverso.py
   ```

4. Verifique:
   ```bash
   python application/verificar_etl_reverso.py
   ```

5. Quando tudo passar, veja o relatório de verdade:
   ```bash
   streamlit run application/app.py
   ```
   Isso abre uma aba no navegador com KPIs, gráficos de barra e tabelas
   — tudo lido direto de `database.sqlite`.

## Ferramentas de desenvolvimento (fora do exercício)

`dev_cli.py` é um CLI com três comandos, útil pra quem está
desenvolvendo/revisando o projeto -- não faz parte do que o aluno
precisa entregar:

```bash
python application/dev_cli.py criar     # cria database.sqlite com as 4 tabelas vazias
python application/dev_cli.py popular   # (re)cria o banco e insere dados fictícios
python application/dev_cli.py limpar    # apaga os DADOS das tabelas (mantém arquivo/schema)
python application/dev_cli.py --help    # lista os comandos
```

`popular` é útil pra testar `app.py` rapidamente sem passar pelo
pipeline. `limpar` só roda `DELETE FROM` em cada tabela -- para apagar o
banco por completo, apague `database.sqlite` diretamente.

## Tabelas esperadas em `database.sqlite`

Uma tabela por CSV de `lakehouse/gold/saida/`, com as mesmas colunas:

```
resumo_vendas_categoria (categoria, quantidade_vendida, valor_total)
vendas_por_mes          (mes, quantidade_vendas, valor_total)
top_clientes            (id_cliente, nome, valor_total)
resumo_geral            (total_vendas, valor_total_geral, ticket_medio)
```
