# landing/

Esta é a **zona de pouso** (landing zone): os arquivos exatamente como
"chegaram" de fora, sem nenhum tratamento. Você não deve editar nada
aqui — esta pasta é só leitura para o exercício.

| Arquivo         | Formato                | O que representa                          |
|------------------|-------------------------|--------------------------------------------|
| `vendas.csv`     | CSV separado por vírgula | Exportação das vendas da loja              |
| `clientes.json`  | JSON (lista de objetos)  | Cadastro de clientes                       |
| `produtos.txt`   | Texto delimitado por `\|` | Catálogo de produtos (sistema legado)      |

Cada um desses arquivos tem problemas de qualidade de dados DE PROPÓSITO
(valores ausentes, formatos inconsistentes, duplicatas, etc.) — isso é o
próprio exercício! Sua tarefa começa em [`../bronze/`](../bronze/README.md):
leia esses três arquivos e monte a camada bronze.

Dê uma olhada nos arquivos com um editor de texto antes de começar a
programar. Tente responder, só olhando:
  - `vendas.csv`: as datas estão todas no mesmo formato? Todo valor está
    preenchido?
  - `clientes.json`: todo registro tem as mesmas chaves? Os e-mails têm
    todos um formato razoável?
  - `produtos.txt`: quantas colunas cada linha tem? Existem linhas que
    não são dados (comentários, linhas em branco)?
