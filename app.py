import streamlit as st
import pandas as pd
import sqlite3
from faker import Faker
import matplotlib.pyplot as plt

# Interface Streamlit
def main():
    st.title("ERP Financier avec Streamlit")
    
    menu = ["Clients", "Factures à Payer", "Factures à Recevoir", "Écritures", "Rapports", "Flux de Trésorerie"]
    choice = st.sidebar.selectbox("Sélectionnez une option", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clients":
        st.subheader("Enregistrement des Clients")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Factures à Payer":
        st.subheader("Factures à Payer")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Factures à Recevoir":
        st.subheader("Factures à Recevoir")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Écritures":
        st.subheader("Écritures Financières")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Rapports":
        st.subheader("Rapport de Flux de Trésorerie")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)
        
        # Graphique de flux de trésorerie
        if not df.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            types = df["tipo"].tolist()
            totaux = df["total"].tolist()
            couleurs = ["green" if t.lower() == "receita" else "red" for t in types]
            
            ax.bar(types, totaux, color=couleurs)
            ax.set_title("Rapport de Flux de Trésorerie")
            ax.set_ylabel("Total (€)")
            
            for i, total in enumerate(totaux):
                ax.text(i, total + 2000, f"€ {total:,.2f}", ha="center", fontsize=12)
            
            st.pyplot(fig)
        else:
            st.write("Aucune donnée disponible à afficher.")
        
        # Graphique de distribution des factures à payer par fournisseur
        st.subheader("Répartition des Factures à Payer par Fournisseur")
        df_fournisseurs = pd.read_sql_query(
            "SELECT fornecedor, SUM(valor) as total FROM contas_pagar GROUP BY fornecedor ORDER BY total DESC LIMIT 4", conn)
        
        if not df_fournisseurs.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(df_fournisseurs["total"], labels=df_fournisseurs["fornecedor"], autopct='%1.1f%%', startangle=140)
            ax.set_title("Répartition des Factures à Payer (Top 4 Fournisseurs)")
            st.pyplot(fig)
        else:
            st.write("Aucune donnée disponible à afficher.")
        
        # Graphique du statut des factures à payer et à recevoir
        st.subheader("Statut des Factures à Payer et à Recevoir")
        df_statut_payer = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_pagar GROUP BY status", conn)
        df_statut_recevoir = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_receber GROUP BY status", conn)
        
        if not df_statut_payer.empty and not df_statut_recevoir.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            labels_statut = ["En attente", "Payées/Reçues"]
            valeurs_payer = [
                df_statut_payer[df_statut_payer["status"] == "Pendente"]["total"].sum(),
                df_statut_payer[df_statut_payer["status"] == "Pago"]["total"].sum()
            ]
            valeurs_recevoir = [
                df_statut_recevoir[df_statut_recevoir["status"] == "Pendente"]["total"].sum(),
                df_statut_recevoir[df_statut_recevoir["status"] == "Recebido"]["total"].sum()
            ]
            
            ax.bar(labels_statut, valeurs_payer, label="À Payer", alpha=0.7, color="red")
            ax.bar(labels_statut, valeurs_recevoir, label="À Recevoir", alpha=0.7, color="green", bottom=valeurs_payer)
            ax.set_title("Statut des Factures à Payer et à Recevoir")
            ax.set_ylabel("Total (€)")
            ax.legend()
            st.pyplot(fig)
        else:
            st.write("Aucune donnée disponible à afficher.")
        
        # Top 5 clients avec le plus de revenus
        st.subheader("Top 5 Clients avec le Plus de Revenus")
        df_top_clients = pd.read_sql_query("""
            SELECT c.nome, SUM(cr.valor) as total 
            FROM contas_receber cr 
            JOIN clientes c ON cr.cliente_id = c.id 
            WHERE cr.status = 'Recebido' 
            GROUP BY c.nome 
            ORDER BY total DESC 
            LIMIT 5""", conn)
        
        if not df_top_clients.empty:
            st.dataframe(df_top_clients)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(df_top_clients["nome"], df_top_clients["total"], color="blue")
            ax.set_title("Top 5 Clients avec le Plus de Revenus")
            ax.set_ylabel("Total (€)")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.write("Aucune donnée disponible à afficher.")
        
        # Comparaison recette vs dépense du mois actuel
        st.subheader("Comparaison Recette vs Dépense - Mois en cours")
        df_comparaison = pd.read_sql_query("""
            SELECT tipo, SUM(valor) as total 
            FROM lancamentos 
            WHERE strftime('%Y-%m', data) = strftime('%Y-%m', 'now')
            GROUP BY tipo""", conn)
        
        if not df_comparaison.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            couleurs = ["green" if t == "Receita" else "red" for t in df_comparaison["tipo"]]
            ax.bar(df_comparaison["tipo"], df_comparaison["total"], color=couleurs)
            ax.set_title("Recette vs Dépense - Mois en cours")
            ax.set_ylabel("Total (€)")
            st.pyplot(fig)
        else:
            st.write("Aucune donnée disponible à afficher.")
        
        # Prévision du flux de trésorerie à 30 jours
        st.subheader("Prévision de Trésorerie (Prochains 30 Jours)")
        df_prevision = pd.read_sql_query("""
            SELECT 'Factures à Payer' as tipo, SUM(valor) as total 
            FROM contas_pagar 
            WHERE vencimento BETWEEN date('now') AND date('now', '+30 days')
            UNION ALL
            SELECT 'Factures à Recevoir' as tipo, SUM(valor) as total 
            FROM contas_receber 
            WHERE vencimento BETWEEN date('now') AND date('now', '+30 days')""", conn)
        
        if not df_prevision.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            couleurs = ["red" if t == "Factures à Payer" else "green" for t in df_prevision["tipo"]]
            ax.bar(df_prevision["tipo"], df_prevision["total"], color=couleurs)
            ax.set_title("Prévision de Trésorerie - Prochains 30 Jours")
            ax.set_ylabel("Total (€)")
            st.pyplot(fig)
        else:
            st.write("Aucune donnée disponible à afficher.")

if __name__ == "__main__":
    main()
