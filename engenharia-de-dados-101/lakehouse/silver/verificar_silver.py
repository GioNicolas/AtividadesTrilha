"""
verificar_silver.py
======================

Script de verificação da camada SILVER. Não precisa editar -- rode com:
    python lakehouse/silver/verificar_silver.py

Ele confere, para os 3 arquivos em lakehouse/silver/saida/:
  1. Existência e colunas esperadas.
  2. Ausência de chaves primárias duplicadas (id_cliente, id_produto, id_venda).
  3. Campos obrigatórios preenchidos (nada de vazio nos campos-chave).
  4. Formatos válidos: datas em AAAA-MM-DD, números realmente numéricos,
     e-mails com formato plausível, categorias e estados dentro da lista
     de valores oficiais.
  5. Integridade referencial: toda venda aponta para um id_cliente e um
     id_produto que realmente existem nos outros dois arquivos.

Todas as checagens são feitas COMPARANDO OS SEUS PRÓPRIOS ARQUIVOS entre
si (não existe uma "resposta certa" única de quantas linhas devem
sobreviver à limpeza -- o que importa é que o resultado final seja
consistente e siga as regras do README).
"""

import csv
import re
import sys
from pathlib import Path

SAIDA = Path(__file__).parent / "saida"

CATEGORIAS_VALIDAS = {"Eletrônicos", "Livros", "Roupas", "Alimentos", "Brinquedos"}
ESTADOS_VALIDOS = {"SP", "RJ", "MG", "RS", "BA", "PR", "PE", "CE", "SC", "GO"}
REGEX_DATA_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

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


def ler_csv(nome: str) -> list[dict] | None:
    caminho = SAIDA / nome
    if not caminho.exists():
        checar(False, "", f"{caminho} não existe. Rode 'python lakehouse/silver/transformacao.py' primeiro.")
        return None
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def eh_numero(valor: str) -> bool:
    try:
        float(valor)
        return True
    except (TypeError, ValueError):
        return False


def checar_sem_duplicatas(linhas: list[dict], coluna: str, nome_arquivo: str) -> None:
    valores = [l[coluna] for l in linhas]
    duplicados = {v for v in valores if valores.count(v) > 1}
    checar(
        not duplicados,
        f"nenhum '{coluna}' duplicado em {nome_arquivo}.",
        f"'{coluna}' duplicado(s) em {nome_arquivo}: {sorted(duplicados)[:10]}",
    )


def checar_campos_obrigatorios(linhas: list[dict], colunas: list[str], nome_arquivo: str) -> None:
    for coluna in colunas:
        vazios = sum(1 for l in linhas if not str(l.get(coluna, "")).strip())
        checar(
            vazios == 0,
            f"coluna '{coluna}' sem valores vazios em {nome_arquivo}.",
            f"coluna '{coluna}' tem {vazios} valor(es) vazio(s) em {nome_arquivo}.",
        )


def verificar_clientes() -> set:
    print("\n--- clientes_silver.csv ---")
    linhas = ler_csv("clientes_silver.csv")
    if linhas is None:
        return set()

    checar_campos_obrigatorios(linhas, ["id_cliente", "nome", "email", "estado"], "clientes_silver.csv")
    checar_sem_duplicatas(linhas, "id_cliente", "clientes_silver.csv")

    emails_invalidos = [l["email"] for l in linhas if not REGEX_EMAIL.match(l.get("email", ""))]
    checar(
        not emails_invalidos,
        "todos os e-mails têm formato válido.",
        f"{len(emails_invalidos)} e-mail(s) com formato inválido, ex.: {emails_invalidos[:5]}",
    )

    estados_invalidos = [l["estado"] for l in linhas if l.get("estado") not in ESTADOS_VALIDOS]
    checar(
        not estados_invalidos,
        "todos os estados são siglas válidas (2 letras maiúsculas).",
        f"{len(estados_invalidos)} estado(s) fora do padrão, ex.: {estados_invalidos[:5]}",
    )

    return {l["id_cliente"] for l in linhas}


def verificar_produtos() -> set:
    print("\n--- produtos_silver.csv ---")
    linhas = ler_csv("produtos_silver.csv")
    if linhas is None:
        return set()

    checar_campos_obrigatorios(linhas, ["id_produto", "nome", "categoria", "preco", "ativo"], "produtos_silver.csv")
    checar_sem_duplicatas(linhas, "id_produto", "produtos_silver.csv")

    categorias_invalidas = [l["categoria"] for l in linhas if l.get("categoria") not in CATEGORIAS_VALIDAS]
    checar(
        not categorias_invalidas,
        "todas as categorias batem com a lista oficial.",
        f"{len(categorias_invalidas)} categoria(s) fora do padrão, ex.: {categorias_invalidas[:5]}. "
        f"Válidas: {sorted(CATEGORIAS_VALIDAS)}",
    )

    precos_invalidos = [l["preco"] for l in linhas if not eh_numero(l.get("preco")) or float(l["preco"]) <= 0]
    checar(
        not precos_invalidos,
        "todos os preços são números positivos.",
        f"{len(precos_invalidos)} preço(s) inválido(s), ex.: {precos_invalidos[:5]}",
    )

    ativos_invalidos = [l["ativo"] for l in linhas if l.get("ativo") not in {"0", "1"}]
    checar(
        not ativos_invalidos,
        "coluna 'ativo' contém apenas 0 ou 1.",
        f"{len(ativos_invalidos)} valor(es) inválido(s) em 'ativo', ex.: {ativos_invalidos[:5]}",
    )

    return {l["id_produto"] for l in linhas}


def verificar_vendas(ids_clientes_validos: set, ids_produtos_validos: set) -> None:
    print("\n--- vendas_silver.csv ---")
    linhas = ler_csv("vendas_silver.csv")
    if linhas is None:
        return

    checar_campos_obrigatorios(
        linhas, ["id_venda", "id_cliente", "id_produto", "quantidade", "data_venda", "valor_total"], "vendas_silver.csv"
    )
    checar_sem_duplicatas(linhas, "id_venda", "vendas_silver.csv")

    datas_invalidas = [l["data_venda"] for l in linhas if not REGEX_DATA_ISO.match(l.get("data_venda", ""))]
    checar(
        not datas_invalidas,
        "todas as datas estão no formato AAAA-MM-DD.",
        f"{len(datas_invalidas)} data(s) fora do padrão, ex.: {datas_invalidas[:5]}",
    )

    quantidades_invalidas = [
        l["quantidade"] for l in linhas
        if not l.get("quantidade", "").lstrip("-").isdigit() or int(l["quantidade"]) <= 0
    ]
    checar(
        not quantidades_invalidas,
        "todas as quantidades são inteiros positivos.",
        f"{len(quantidades_invalidas)} quantidade(s) inválida(s), ex.: {quantidades_invalidas[:5]}",
    )

    valores_invalidos = [l["valor_total"] for l in linhas if not eh_numero(l.get("valor_total")) or float(l["valor_total"]) <= 0]
    checar(
        not valores_invalidos,
        "todos os valores totais são números positivos.",
        f"{len(valores_invalidos)} valor(es) inválido(s), ex.: {valores_invalidos[:5]}",
    )

    if ids_clientes_validos:
        clientes_orfaos = [l["id_cliente"] for l in linhas if l.get("id_cliente") not in ids_clientes_validos]
        checar(
            not clientes_orfaos,
            "todo id_cliente em vendas existe em clientes_silver.",
            f"{len(clientes_orfaos)} venda(s) referenciam id_cliente inexistente, ex.: {clientes_orfaos[:5]}",
        )

    if ids_produtos_validos:
        produtos_orfaos = [l["id_produto"] for l in linhas if l.get("id_produto") not in ids_produtos_validos]
        checar(
            not produtos_orfaos,
            "todo id_produto em vendas existe em produtos_silver.",
            f"{len(produtos_orfaos)} venda(s) referenciam id_produto inexistente, ex.: {produtos_orfaos[:5]}",
        )


def main() -> None:
    print("Verificando camada SILVER...")
    ids_clientes = verificar_clientes()
    ids_produtos = verificar_produtos()
    verificar_vendas(ids_clientes, ids_produtos)

    print(f"\n{'=' * 60}")
    if falhas == 0:
        print(f"TUDO CERTO! {total_checagens}/{total_checagens} checagens passaram.")
        print("Pode seguir para a camada gold.")
        sys.exit(0)
    else:
        print(f"{falhas} de {total_checagens} checagem(ns) FALHARAM. Corrija e rode novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
