"""
verificar_bronze.py
=====================

Script de verificação da camada BRONZE. Você NÃO precisa (nem deve) editar
este arquivo -- ele já está pronto e é o "juiz" que confere se a sua
ingestão em `ingestao.py` está correta.

Rode com:
    python lakehouse/bronze/verificar_bronze.py

O que ele confere, para cada um dos 3 arquivos de saída em lakehouse/bronze/saida/:
  1. O arquivo existe e é um CSV válido.
  2. Ele tem as colunas esperadas, incluindo "arquivo_origem" e "dt_ingestao".
  3. O NÚMERO DE LINHAS bate exatamente com o número de registros da
     landing (bronze não pode perder nem inventar registros -- inclusive
     duplicatas devem ser mantidas, isso é trabalho da silver!).
  4. "arquivo_origem" e "dt_ingestao" estão preenchidos em toda linha.

Se alguma checagem falhar, leia a mensagem: ela te diz exatamente o que
está errado e em qual arquivo.
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

LAKEHOUSE = Path(__file__).parent.parent
LANDING = LAKEHOUSE / "landing"
SAIDA = Path(__file__).parent / "saida"

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


def ler_csv(caminho: Path) -> list[dict]:
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def contar_linhas_landing_csv() -> int:
    with open(LANDING / "vendas.csv", newline="", encoding="utf-8") as arquivo:
        linhas = list(csv.reader(arquivo))
    return len(linhas) - 1  # menos o cabeçalho


def contar_registros_landing_json() -> int:
    with open(LANDING / "clientes.json", encoding="utf-8") as arquivo:
        return len(json.load(arquivo))


def contar_linhas_landing_txt() -> int:
    with open(LANDING / "produtos.txt", encoding="utf-8") as arquivo:
        linhas_uteis = [
            linha.strip() for linha in arquivo
            if linha.strip() and not linha.strip().startswith("#")
        ]
    # a primeira linha útil é o cabeçalho, o resto são dados
    return len(linhas_uteis) - 1


def checar_arquivo(nome_arquivo: str, colunas_esperadas: list[str], qtd_esperada: int) -> None:
    print(f"\n--- {nome_arquivo} ---")
    caminho = SAIDA / nome_arquivo

    if not caminho.exists():
        checar(False, "", f"arquivo {caminho} não existe. Rode 'python lakehouse/bronze/ingestao.py' primeiro.")
        return
    checar(True, f"arquivo {nome_arquivo} existe.", "")

    linhas = ler_csv(caminho)

    colunas_encontradas = set(linhas[0].keys()) if linhas else set()
    faltando = set(colunas_esperadas) - colunas_encontradas
    checar(
        not faltando,
        f"todas as colunas esperadas estão presentes ({', '.join(colunas_esperadas)}).",
        f"faltam colunas: {sorted(faltando)}. Encontradas: {sorted(colunas_encontradas)}",
    )

    checar(
        len(linhas) == qtd_esperada,
        f"quantidade de linhas está correta ({len(linhas)}).",
        f"esperado {qtd_esperada} linhas (igual à landing), mas encontrei {len(linhas)}. "
        f"Lembre-se: a bronze preserva TODAS as linhas da landing, inclusive duplicadas.",
    )

    origem_vazia = [i for i, l in enumerate(linhas) if not l.get("arquivo_origem")]
    checar(
        not origem_vazia,
        "coluna 'arquivo_origem' preenchida em todas as linhas.",
        f"'arquivo_origem' vazia em {len(origem_vazia)} linha(s).",
    )

    def timestamp_valido(valor: str) -> bool:
        try:
            datetime.fromisoformat(valor)
            return True
        except (ValueError, TypeError):
            return False

    invalidos = [i for i, l in enumerate(linhas) if not timestamp_valido(l.get("dt_ingestao", ""))]
    checar(
        not invalidos,
        "coluna 'dt_ingestao' preenchida com data/hora válida em todas as linhas.",
        f"'dt_ingestao' ausente ou inválida em {len(invalidos)} linha(s).",
    )


def main() -> None:
    print("Verificando camada BRONZE...")

    checar_arquivo(
        "vendas_bronze.csv",
        ["id_venda", "id_cliente", "id_produto", "quantidade", "data_venda", "valor_total", "arquivo_origem", "dt_ingestao"],
        contar_linhas_landing_csv(),
    )
    checar_arquivo(
        "clientes_bronze.csv",
        ["id_cliente", "nome", "email", "cidade", "estado", "arquivo_origem", "dt_ingestao"],
        contar_registros_landing_json(),
    )
    checar_arquivo(
        "produtos_bronze.csv",
        ["id_produto", "nome", "categoria", "preco", "ativo", "arquivo_origem", "dt_ingestao"],
        contar_linhas_landing_txt(),
    )

    print(f"\n{'=' * 60}")
    if falhas == 0:
        print(f"TUDO CERTO! {total_checagens}/{total_checagens} checagens passaram.")
        print("Pode seguir para a camada silver.")
        sys.exit(0)
    else:
        print(f"{falhas} de {total_checagens} checagem(ns) FALHARAM. Corrija e rode novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
