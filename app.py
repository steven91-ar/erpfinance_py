import streamlit as st
import pandas as pd
import sqlite3
from faker import Faker
import matplotlib.pyplot as plt

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios", "Fluxo de Caixa"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)
        
        # Criar gráfico de fluxo de caixa
        if not df.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            tipos = df["tipo"].tolist()
            totais = df["total"].tolist()
            cores = ["green" if tipo.lower() == "receita" else "red" for tipo in tipos]
            
            ax.bar(tipos, totais, color=cores)
            ax.set_title("Relatório de Fluxo de Caixa")
            ax.set_ylabel("Total (R$)")
            
            for i, total in enumerate(totais):
                ax.text(i, total + 2000, f"R$ {total:,.2f}", ha="center", fontsize=12)
            
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível para exibição.")
        
        # Criar gráfico de distribuição das contas a pagar por fornecedor
        st.subheader("Distribuição das Contas a Pagar por Fornecedor")
        df_fornecedores = pd.read_sql_query("SELECT fornecedor, SUM(valor) as total FROM contas_pagar GROUP BY fornecedor ORDER BY total DESC LIMIT 4", conn)
        
        if not df_fornecedores.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(df_fornecedores["total"], labels=df_fornecedores["fornecedor"], autopct='%1.1f%%', startangle=140)
            ax.set_title("Distribuição das Contas a Pagar (Top 4 Fornecedores)")
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível para exibição.")
        
        # Criar gráfico de status das contas a pagar e a receber
        st.subheader("Status das Contas a Pagar e Receber")
        df_status_pagar = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_pagar GROUP BY status", conn)
        df_status_receber = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_receber GROUP BY status", conn)
        
        if not df_status_pagar.empty and not df_status_receber.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            status_labels = ["Pendentes", "Pagas/Recebidas"]
            valores_pagar = [
                df_status_pagar[df_status_pagar["status"] == "Pendente"]["total"].sum(),
                df_status_pagar[df_status_pagar["status"] == "Pago"]["total"].sum()
            ]
            valores_receber = [
                df_status_receber[df_status_receber["status"] == "Pendente"]["total"].sum(),
                df_status_receber[df_status_receber["status"] == "Recebido"]["total"].sum()
            ]
            
            ax.bar(status_labels, valores_pagar, label="Contas a Pagar", alpha=0.7, color="red")
            ax.bar(status_labels, valores_receber, label="Contas a Receber", alpha=0.7, color="green", bottom=valores_pagar)
            ax.set_title("Status das Contas a Pagar e Receber")
            ax.set_ylabel("Total (R$)")
            ax.legend()
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível para exibição.")
        
        # Criar gráfico dos Top 5 Clientes com Maior Receita
        st.subheader("Top 5 Clientes com Maior Receita")
        df_top_clientes = pd.read_sql_query("""
            SELECT c.nome, SUM(cr.valor) as total 
            FROM contas_receber cr 
            JOIN clientes c ON cr.cliente_id = c.id 
            WHERE cr.status = 'Recebido' 
            GROUP BY c.nome 
            ORDER BY total DESC 
            LIMIT 5""", conn)
        
        if not df_top_clientes.empty:
            st.dataframe(df_top_clientes)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(df_top_clientes["nome"], df_top_clientes["total"], color="blue")
            ax.set_title("Top 5 Clientes com Maior Receita")
            ax.set_ylabel("Total (R$)")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível para exibição.")

                # Criar gráfico de comparação entre receita e despesa do mês atual
        st.subheader("Comparação Receita vs Despesa - Mês Atual")
        df_comparacao = pd.read_sql_query("""
            SELECT tipo, SUM(valor) as total 
            FROM lancamentos 
            WHERE strftime('%Y-%m', data) = strftime('%Y-%m', 'now')
            GROUP BY tipo""", conn)
        
        if not df_comparacao.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(df_comparacao["tipo"], df_comparacao["total"], color=["green" if tipo == "Receita" else "red" for tipo in df_comparacao["tipo"]])
            ax.set_title("Receita vs Despesa - Mês Atual")
            ax.set_ylabel("Total (R$)")
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível para exibição.")
        
        # Criar gráfico de previsão de fluxo de caixa
        st.subheader("Previsão de Fluxo de Caixa (Próximos 30 Dias)")
        df_previsao = pd.read_sql_query("""
            SELECT 'Contas a Pagar' as tipo, SUM(valor) as total 
            FROM contas_pagar 
            WHERE vencimento BETWEEN date('now') AND date('now', '+30 days')
            UNION ALL
            SELECT 'Contas a Receber' as tipo, SUM(valor) as total 
            FROM contas_receber 
            WHERE vencimento BETWEEN date('now') AND date('now', '+30 days')""", conn)
        
        if not df_previsao.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(df_previsao["tipo"], df_previsao["total"], color=["red" if tipo == "Contas a Pagar" else "green" for tipo in df_previsao["tipo"]])
            ax.set_title("Previsão de Fluxo de Caixa - Próximos 30 Dias")
            ax.set_ylabel("Total (R$)")
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível para exibição.")

if __name__ == "__main__":
    main()
