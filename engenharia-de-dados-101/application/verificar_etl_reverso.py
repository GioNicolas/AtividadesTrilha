"""
verificar_etl_reverso.py
===========================

Verifica a carga feita em `etl_reverso.py`. Não precisa editar -- rode
com:
    python application/verificar_etl_reverso.py

Ele confere, para cada uma das 4 tabelas esperadas em `database.sqlite`:
  1. A tabela existe e tem as colunas certas.
  2. O número de linhas bate exatamente com o CSV correspondente em
     `lakehouse/gold/saida/` (a carga não pode perder nem inventar
     linhas -- é cópia direta, sem agregação).
  3. Os valores de cada linha batem com os do CSV, na mesma ordem
     (permitindo pequena tolerância numérica por causa de arredondamento).
"""

import csv
import sqlite3
import sys
from pathlib import Path

GOLD_SAIDA = Path(__file__).parent.parent / "lakehouse" / "gold" / "saida"
BANCO = Path(__file__).parent / "database.sqlite"

TABELAS = {
    "resumo_vendas_categoria": ["categoria", "quantidade_vendida", "valor_total"],
    "vendas_por_mes": ["mes", "quantidade_vendas", "valor_total"],
    "top_clientes": ["id_cliente", "nome", "valor_total"],
    "resumo_geral": ["total_vendas", "valor_total_geral", "ticket_medio"],
}

TOLERANCIA = 0.01

total_checagens = 0
falhas = 0


def checar(condicao: bool, ok: str, erro: str) -> None:
    global total_checagens, falhas
    total_checagens += 1
    if condicao:
        print(f"  [OK] {ok}")
    else:
        falhas += 1
        print(f"  [FALHOU] {erro}")


def valores_batem(a: str, b: str) -> bool:
    """Compara dois valores vindos de CSV/SQLite, com tolerância para números."""
    if a == b:
        return True
    try:
        return abs(float(a) - float(b)) <= TOLERANCIA
    except (TypeError, ValueError):
        return False


def ler_csv_gold(nome_tabela: str) -> list[dict] | None:
    caminho = GOLD_SAIDA / f"{nome_tabela}.csv"
    if not caminho.exists():
        checar(False, "", f"{caminho} não existe. Rode 'python lakehouse/gold/agregacao.py' primeiro.")
        return None
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def main() -> None:
    print("Verificando o ETL reverso (application/database.sqlite)...")

    if not BANCO.exists():
        print(f"\n[FALHOU] {BANCO} não existe. Rode 'python application/etl_reverso.py' primeiro.")
        sys.exit(1)

    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row

    for nome_tabela, colunas in TABELAS.items():
        print(f"\n--- {nome_tabela} ---")

        csv_linhas = ler_csv_gold(nome_tabela)
        if csv_linhas is None:
            continue

        try:
            db_linhas = [dict(l) for l in conexao.execute(f"SELECT * FROM {nome_tabela}")]
        except sqlite3.OperationalError:
            checar(False, "", f"tabela '{nome_tabela}' não existe em database.sqlite.")
            continue
        checar(True, f"tabela '{nome_tabela}' existe.", "")

        colunas_encontradas = set(db_linhas[0].keys()) if db_linhas else set()
        faltando = set(colunas) - colunas_encontradas
        checar(
            not faltando,
            f"todas as colunas esperadas estão presentes ({', '.join(colunas)}).",
            f"faltam colunas: {sorted(faltando)}. Encontradas: {sorted(colunas_encontradas)}",
        )

        checar(
            len(db_linhas) == len(csv_linhas),
            f"quantidade de linhas está correta ({len(db_linhas)}).",
            f"esperado {len(csv_linhas)} linhas (igual ao CSV), mas encontrei {len(db_linhas)}.",
        )

        divergencias = 0
        for i, (csv_linha, db_linha) in enumerate(zip(csv_linhas, db_linhas)):
            for coluna in colunas:
                if not valores_batem(str(csv_linha.get(coluna, "")), str(db_linha.get(coluna, ""))):
                    divergencias += 1
        checar(
            divergencias == 0,
            "todos os valores batem com o CSV de origem, na mesma ordem.",
            f"{divergencias} valor(es) divergem do CSV de origem -- confira se inserir_linhas() "
            f"está preservando a ordem e os valores originais.",
        )

    conexao.close()

    print(f"\n{'=' * 60}")
    if falhas == 0:
        print(f"TUDO CERTO! {total_checagens}/{total_checagens} checagens passaram.")
        print("Agora rode: streamlit run application/app.py")
        sys.exit(0)
    else:
        print(f"{falhas} de {total_checagens} checagem(ns) FALHARAM. Corrija e rode novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
