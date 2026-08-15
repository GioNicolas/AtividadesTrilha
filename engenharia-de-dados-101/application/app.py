"""
app.py - Relatório da Loja Boa Compra
========================================

Este arquivo já está PRONTO -- você não precisa mexer nele. Ele só lê as
tabelas de `database.sqlite` (carregadas por `etl_reverso.py` a partir da
camada gold) e monta um relatório visual com Streamlit. Não há nenhuma
agregação aqui -- os números já vêm prontos da gold, isso aqui é só
apresentação.

Para rodar:
    streamlit run application/app.py

Se aparecer um aviso pedindo para rodar o ETL reverso primeiro, é porque
`application/database.sqlite` ainda não existe ou está incompleto.
"""

import sqlite3
from pathlib import Path

import streamlit as st

BANCO = Path(__file__).parent / "database.sqlite"

st.set_page_config(page_title="Loja Boa Compra - Relatório de Vendas", page_icon="📊", layout="wide")

st.title("📊 Relatório de Vendas - Loja Boa Compra")
st.caption(
    "Este relatório lê direto de `application/database.sqlite`, carregado a partir dos CSVs de "
    "`lakehouse/gold/saida/` por `application/etl_reverso.py`."
)

if not BANCO.exists():
    st.warning(
        "`application/database.sqlite` ainda não existe.\n\n"
        "Rode `python application/etl_reverso.py` e depois "
        "`python application/verificar_etl_reverso.py` antes de abrir este relatório."
    )
    st.stop()

try:
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    resumo = dict(conexao.execute("SELECT * FROM resumo_geral").fetchone())
    por_categoria = [dict(l) for l in conexao.execute("SELECT * FROM resumo_vendas_categoria ORDER BY valor_total DESC")]
    por_mes = [dict(l) for l in conexao.execute("SELECT * FROM vendas_por_mes ORDER BY mes ASC")]
    top_10_clientes = [dict(l) for l in conexao.execute("SELECT * FROM top_clientes ORDER BY valor_total DESC")]
    conexao.close()
except Exception as erro:  # noqa: BLE001
    st.error(
        f"Não foi possível ler `database.sqlite`: {erro}\n\n"
        "Rode `python application/verificar_etl_reverso.py` para conferir se a carga está correta."
    )
    st.stop()

# --- KPIs principais -------------------------------------------------------
coluna1, coluna2, coluna3 = st.columns(3)
coluna1.metric("Total de vendas", f"{int(resumo['total_vendas']):,}".replace(",", "."))
coluna2.metric("Faturamento total", f"R$ {float(resumo['valor_total_geral']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
coluna3.metric("Ticket médio", f"R$ {float(resumo['ticket_medio']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

# --- Vendas por categoria ---------------------------------------------------
st.subheader("Faturamento por categoria")
if por_categoria:
    st.bar_chart(por_categoria, x="categoria", y="valor_total")
    st.dataframe(por_categoria, use_container_width=True, hide_index=True)
else:
    st.info("Sem dados de categoria.")

st.divider()

# --- Vendas por mês ----------------------------------------------------------
st.subheader("Faturamento por mês")
if por_mes:
    st.bar_chart(por_mes, x="mes", y="valor_total")
    st.dataframe(por_mes, use_container_width=True, hide_index=True)
else:
    st.info("Sem dados mensais.")

st.divider()

# --- Top clientes -------------------------------------------------------------
st.subheader("Top 10 clientes")
if top_10_clientes:
    st.dataframe(top_10_clientes, use_container_width=True, hide_index=True)
else:
    st.info("Sem dados de clientes.")
