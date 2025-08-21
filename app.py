import streamlit as st
import pandas as pd
import plotly.express as px

from utils.cleaner import pulisci_csv_big_ambitions
from utils.analyzer import estrai_business_da_revenue
from utils.visualizer import crea_revenue_trend
from utils.visualizer import crea_wage_trend
from utils.analyzer import crea_p_l





st.set_page_config(
    page_title="Big Abmitions Analyzer",
    page_icon="🎮",
    layout="wide"
)


st.title("🎮 Big Ambitions Business Analyzer")
st.write("Analize you business data from Big Ambitions")


# Upload file
uploaded_file = st.file_uploader(
    "Carica il tuo file csv", 
    type=['csv'],
    help="Esporta il file dal gioco e caricalo qui"
)

if uploaded_file is not None:
    # Pulisci il file
    with st.spinner('Pulizia file in corso...'):
        df, errore = pulisci_csv_big_ambitions(uploaded_file)
    
    if errore:
        st.error(f"❌ {errore}")
    else:
        st.success("✅ File pulito con successo!")
        
        # Mostra preview
        st.subheader("📊 Anteprima dati puliti:")
        st.dataframe(df.head(10))
        
        # Mostra statistiche base
        st.subheader("📈 Statistiche base:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Righe totali", len(df))
        with col2:
            st.metric("Tipi di transazione", df['type'].nunique())
        with col3:
            business_names, revenue_per_business, revenue_df = estrai_business_da_revenue(df)
            st.metric("Business trovati", len(business_names))

        if revenue_per_business is not None:
            fig = px.bar(
                x=revenue_per_business.index,
                y= revenue_per_business.values,
                title= "Revenue per Business",
                #Cercare di implementare successivamente un metodo per avere la valuta usata in game (€,$ ecc..)
                labels={"x":"Business", "y":"Revenue"},
                color=revenue_per_business.values,
                color_continuous_scale="viridis"
            )
            fig.update_yaxes(tickformat=",.")
            fig.update_layout(
                height=500,
                showlegend=False,
                font=dict(size=14)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend temporale 
            fig_trend = crea_revenue_trend(revenue_df)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.subheader("💸 Analisi Costi Stipendi")
            col1, col2, col3 = st.columns([2,2,6])
            with col1:
                vista_giorno = st.checkbox("Vista per giorno", value=False)
            with col2:
                tipo_grafico = st.radio("📊 Tipo", ["bar", "line"], horizontal=True)
            with col3:
                business_selezionati = st.multiselect(
                    "Filtra per business:",
                    options=business_names,
                    default=business_names
                )
                    
            try:
                fig_wages = crea_wage_trend(
                    df,
                    kind=tipo_grafico,
                    per_day=vista_giorno,
                    per_business=business_selezionati if business_selezionati else None
                )
                st.plotly_chart(fig_wages, use_container_width=True)
            except Exception as e:
                st.error(f"Errore nell'analisi wages: {str(e)}")
                
                
        # Creazione grafico per P&L
        
        st.subheader("💼 Profit & Loss (P&L) - Base")
        
        # Calcoliamo P&L
        p_l_df, costi_generali = crea_p_l(df)
        
        if not p_l_df.empty:
            st.dataframe(
                p_l_df.style.format({
                    "revenue":"€{:,.2f}",
                    "wages":"€{:,.2f}",
                    "marketing":"€{:,.2f}",
                    "delivery":"€{:,.2f}",
                    "profit":"€{:,.2f}",
                    "costi_diretti":"€{:,.2f}",
                    "margine_lordo":"€{:,.2f}"
                }),
                use_container_width=True
            )
        
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Revenue Totale", f"€{p_l_df['revenue'].sum():,.2f}")
            with col2:
                st.metric("💸 Wages Totali", f"€{p_l_df['wages'].sum():,.2f}")
            with col3:
                st.metric("📈 Profitto Totale", f"€{p_l_df['profit'].sum():,.2f}")
            with col4:
                st.metric("Costi Totali", f"€{(p_l_df["delivery"].sum() + p_l_df["costi_diretti"].sum()):,.2f}")
            with col5:
                margin = (p_l_df['profit'].sum() / p_l_df['revenue'].sum() * 100) if p_l_df['revenue'].sum() > 0 else 0
                st.metric("📊 Margine %", f"{margin:.1f}%")
        else:
            st.warning("Nessun dato disponibile per il P&L")        
else:
    st.info("👆 Carica un file CSV per iniziare l'analisi")