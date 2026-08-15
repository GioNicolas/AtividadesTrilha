"""
dev_cli.py - CLI de ferramentas de desenvolvimento
=====================================================

FERRAMENTA DE DESENVOLVIMENTO -- NÃO FAZ PARTE DO EXERCÍCIO.

Reúne os comandos auxiliares para trabalhar com
`application/database.sqlite` por fora do exercício (`etl_reverso.py`):

    python application/dev_cli.py criar     # cria o banco com as tabelas vazias
    python application/dev_cli.py popular   # (re)cria o banco e insere dados fictícios
    python application/dev_cli.py limpar    # apaga os DADOS das tabelas (mantém arquivo/schema)

Se você é aluno: nada disso substitui o exercício -- os dados aqui não
vêm de `lakehouse/gold/saida/`. Use `etl_reverso.py` para o exercício de
verdade.
"""

import argparse
import random
import sqlite3
from pathlib import Path

BANCO = Path(__file__).parent / "database.sqlite"

TABELAS = {
    "resumo_vendas_categoria": ["categoria", "quantidade_vendida", "valor_total"],
    "vendas_por_mes": ["mes", "quantidade_vendas", "valor_total"],
    "top_clientes": ["id_cliente", "nome", "valor_total"],
    "resumo_geral": ["total_vendas", "valor_total_geral", "ticket_medio"],
}

CATEGORIAS = ["Eletrônicos", "Livros", "Roupas", "Alimentos", "Brinquedos"]
MESES = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06"]
NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Elisa", "Fábio", "Gabriela", "Hugo", "Isabela", "João"]
SOBRENOMES = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Ferreira", "Almeida", "Lima", "Gomes"]


# --- criar --------------------------------------------------------------------
def criar_banco() -> None:
    conexao = sqlite3.connect(BANCO)
    for nome_tabela, colunas in TABELAS.items():
        conexao.execute(f"DROP TABLE IF EXISTS {nome_tabela}")
        lista_colunas = ", ".join(colunas)
        conexao.execute(f"CREATE TABLE {nome_tabela} ({lista_colunas})")
    conexao.commit()
    conexao.close()


def comando_criar() -> None:
    criar_banco()
    print(f"Banco criado (tabelas vazias) em: {BANCO}")
    print("Tabelas:", ", ".join(TABELAS))


# --- popular --------------------------------------------------------------------
def gerar_dados(rng: random.Random) -> dict:
    resumo_categoria = []
    for categoria in CATEGORIAS:
        quantidade = rng.randint(20, 120)
        valor = round(quantidade * rng.uniform(30, 150), 2)
        resumo_categoria.append((categoria, quantidade, valor))
    resumo_categoria.sort(key=lambda linha: linha[2], reverse=True)

    vendas_por_mes = []
    for mes in MESES:
        quantidade = rng.randint(30, 80)
        valor = round(quantidade * rng.uniform(150, 300), 2)
        vendas_por_mes.append((mes, quantidade, valor))

    top_clientes = []
    for id_cliente in range(1, 11):
        nome = f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}"
        valor = round(rng.uniform(500, 3000), 2)
        top_clientes.append((id_cliente, nome, valor))
    top_clientes.sort(key=lambda linha: linha[2], reverse=True)

    total_vendas = sum(linha[1] for linha in vendas_por_mes)
    valor_total_geral = round(sum(linha[2] for linha in vendas_por_mes), 2)
    ticket_medio = round(valor_total_geral / total_vendas, 2)
    resumo_geral = [(total_vendas, valor_total_geral, ticket_medio)]

    return {
        "resumo_vendas_categoria": resumo_categoria,
        "vendas_por_mes": vendas_por_mes,
        "top_clientes": top_clientes,
        "resumo_geral": resumo_geral,
    }


def comando_popular() -> None:
    rng = random.Random()  # sem semente fixa -- dados diferentes a cada execução
    criar_banco()
    conexao = sqlite3.connect(BANCO)

    dados = gerar_dados(rng)
    conexao.executemany("INSERT INTO resumo_vendas_categoria VALUES (?, ?, ?)", dados["resumo_vendas_categoria"])
    conexao.executemany("INSERT INTO vendas_por_mes VALUES (?, ?, ?)", dados["vendas_por_mes"])
    conexao.executemany("INSERT INTO top_clientes VALUES (?, ?, ?)", dados["top_clientes"])
    conexao.executemany("INSERT INTO resumo_geral VALUES (?, ?, ?)", dados["resumo_geral"])

    conexao.commit()
    conexao.close()

    print(f"database.sqlite populado com dados fictícios em: {BANCO}")
    print("Rode: streamlit run application/app.py")


# --- limpar --------------------------------------------------------------------
def comando_limpar() -> None:
    if not BANCO.exists():
        print(f"{BANCO} não existe -- nada a limpar.")
        print("Rode 'python application/dev_cli.py criar' para criar o banco primeiro.")
        return

    conexao = sqlite3.connect(BANCO)
    tabelas_existentes = {
        linha[0] for linha in conexao.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }

    for nome_tabela in TABELAS:
        if nome_tabela in tabelas_existentes:
            conexao.execute(f"DELETE FROM {nome_tabela}")
            print(f"{nome_tabela}: dados apagados.")
        else:
            print(f"{nome_tabela}: tabela não existe, ignorando.")

    conexao.commit()
    conexao.close()

    print(f"\nDados limpos em: {BANCO} (arquivo e schema mantidos).")


# --- CLI --------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ferramentas de desenvolvimento para application/database.sqlite (fora do exercício)."
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)
    subparsers.add_parser("criar", help="cria o banco com as 4 tabelas vazias")
    subparsers.add_parser("popular", help="(re)cria o banco e insere dados fictícios")
    subparsers.add_parser("limpar", help="apaga os dados das tabelas (mantém arquivo e schema)")

    args = parser.parse_args()

    comandos = {
        "criar": comando_criar,
        "popular": comando_popular,
        "limpar": comando_limpar,
    }
    comandos[args.comando]()


if __name__ == "__main__":
    main()
