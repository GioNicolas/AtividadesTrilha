"""
verificar_gold.py
====================

Script de verificação da camada GOLD. Não precisa editar -- rode com:
    python lakehouse/gold/verificar_gold.py

Diferente da bronze/silver, aqui não existe uma contagem "mágica" para
comparar. O que este script faz é conferir CONSISTÊNCIA: os números que
aparecem nos seus relatórios agregados (gold) precisam bater com os dados
que estão em lakehouse/silver/saida/vendas_silver.csv, que é a fonte deles.

Ele confere:
  1. Os 4 arquivos existem e têm as colunas certas.
  2. A soma de valor_total em resumo_vendas_categoria.csv bate com a soma
     em vendas_silver.csv (mesma soma total, só que quebrada por categoria).
  3. A soma de quantidade_vendas em vendas_por_mes.csv bate com o total de
     linhas de vendas_silver.csv.
  4. top_clientes.csv tem no máximo 10 linhas e está ordenado do maior
     para o menor valor_total.
  5. resumo_geral.csv tem uma linha só, e total_vendas / valor_total_geral
     / ticket_medio batem com o que dá pra calcular a partir da silver.
"""

import csv
import sys
from pathlib import Path

LAKEHOUSE = Path(__file__).parent.parent
SILVER_SAIDA = LAKEHOUSE / "silver" / "saida"
SAIDA = Path(__file__).parent / "saida"

TOLERANCIA = 1.0  # tolerância de arredondamento em somas de valores em R$

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


def proximo(a: float, b: float, tolerancia: float = TOLERANCIA) -> bool:
    return abs(a - b) <= tolerancia


def ler_csv(caminho: Path, comando_sugerido: str) -> list[dict] | None:
    if not caminho.exists():
        checar(False, "", f"{caminho} não existe. Rode '{comando_sugerido}' primeiro.")
        return None
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def main() -> None:
    print("Verificando camada GOLD...")

    vendas_silver = ler_csv(SILVER_SAIDA / "vendas_silver.csv", "python lakehouse/silver/transformacao.py")
    if vendas_silver is None:
        print("\nNão foi possível carregar lakehouse/silver/saida/vendas_silver.csv. Rode a camada silver primeiro.")
        sys.exit(1)

    total_linhas_silver = len(vendas_silver)
    soma_valor_silver = sum(float(v["valor_total"]) for v in vendas_silver)

    print("\n--- resumo_vendas_categoria.csv ---")
    resumo_categoria = ler_csv(SAIDA / "resumo_vendas_categoria.csv", "python lakehouse/gold/agregacao.py")
    if resumo_categoria is not None:
        checar(
            {"categoria", "quantidade_vendida", "valor_total"} <= set(resumo_categoria[0].keys()) if resumo_categoria else False,
            "colunas esperadas presentes.",
            "faltam colunas em resumo_vendas_categoria.csv.",
        )
        categorias = [r["categoria"] for r in resumo_categoria]
        checar(len(categorias) == len(set(categorias)), "nenhuma categoria duplicada.", "há categorias duplicadas.")
        soma_categorias = sum(float(r["valor_total"]) for r in resumo_categoria)
        checar(
            proximo(soma_categorias, soma_valor_silver),
            f"soma de valor_total ({soma_categorias:.2f}) bate com a silver ({soma_valor_silver:.2f}).",
            f"soma de valor_total ({soma_categorias:.2f}) NÃO bate com a silver ({soma_valor_silver:.2f}).",
        )

    print("\n--- vendas_por_mes.csv ---")
    vendas_por_mes = ler_csv(SAIDA / "vendas_por_mes.csv", "python lakehouse/gold/agregacao.py")
    if vendas_por_mes is not None:
        checar(
            {"mes", "quantidade_vendas", "valor_total"} <= set(vendas_por_mes[0].keys()) if vendas_por_mes else False,
            "colunas esperadas presentes.",
            "faltam colunas em vendas_por_mes.csv.",
        )
        soma_qtd_meses = sum(int(r["quantidade_vendas"]) for r in vendas_por_mes)
        checar(
            soma_qtd_meses == total_linhas_silver,
            f"soma de quantidade_vendas ({soma_qtd_meses}) bate com o total de vendas da silver ({total_linhas_silver}).",
            f"soma de quantidade_vendas ({soma_qtd_meses}) NÃO bate com o total de vendas da silver ({total_linhas_silver}).",
        )
        soma_valor_meses = sum(float(r["valor_total"]) for r in vendas_por_mes)
        checar(
            proximo(soma_valor_meses, soma_valor_silver),
            f"soma de valor_total por mês bate com a silver.",
            f"soma de valor_total por mês ({soma_valor_meses:.2f}) NÃO bate com a silver ({soma_valor_silver:.2f}).",
        )

    print("\n--- top_clientes.csv ---")
    top_clientes = ler_csv(SAIDA / "top_clientes.csv", "python lakehouse/gold/agregacao.py")
    if top_clientes is not None:
        checar(
            {"id_cliente", "nome", "valor_total"} <= set(top_clientes[0].keys()) if top_clientes else False,
            "colunas esperadas presentes.",
            "faltam colunas em top_clientes.csv.",
        )
        checar(len(top_clientes) <= 10, "no máximo 10 clientes listados.", f"encontrei {len(top_clientes)} clientes (esperado <= 10).")
        valores = [float(r["valor_total"]) for r in top_clientes]
        checar(
            valores == sorted(valores, reverse=True),
            "clientes ordenados do maior para o menor valor_total.",
            "clientes NÃO estão ordenados corretamente por valor_total.",
        )

    print("\n--- resumo_geral.csv ---")
    resumo_geral = ler_csv(SAIDA / "resumo_geral.csv", "python lakehouse/gold/agregacao.py")
    if resumo_geral is not None:
        checar(len(resumo_geral) == 1, "arquivo tem exatamente uma linha.", f"arquivo tem {len(resumo_geral)} linhas (esperado 1).")
        if len(resumo_geral) == 1:
            linha = resumo_geral[0]
            checar(
                int(linha["total_vendas"]) == total_linhas_silver,
                f"total_vendas ({linha['total_vendas']}) bate com a silver ({total_linhas_silver}).",
                f"total_vendas ({linha['total_vendas']}) NÃO bate com a silver ({total_linhas_silver}).",
            )
            checar(
                proximo(float(linha["valor_total_geral"]), soma_valor_silver),
                "valor_total_geral bate com a soma da silver.",
                f"valor_total_geral ({linha['valor_total_geral']}) NÃO bate com a soma da silver ({soma_valor_silver:.2f}).",
            )
            ticket_esperado = round(soma_valor_silver / total_linhas_silver, 2)
            checar(
                proximo(float(linha["ticket_medio"]), ticket_esperado, tolerancia=0.1),
                f"ticket_medio ({linha['ticket_medio']}) confere com o esperado (~{ticket_esperado}).",
                f"ticket_medio ({linha['ticket_medio']}) NÃO confere com o esperado (~{ticket_esperado}).",
            )

    print(f"\n{'=' * 60}")
    if falhas == 0:
        print(f"TUDO CERTO! {total_checagens}/{total_checagens} checagens passaram.")
        print("Sua camada gold está pronta. Agora veja a pasta application/.")
        sys.exit(0)
    else:
        print(f"{falhas} de {total_checagens} checagem(ns) FALHARAM. Corrija e rode novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
