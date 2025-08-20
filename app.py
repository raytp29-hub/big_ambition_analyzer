import streamlit as st
import pandas as pd
import plotly.express as px

from utils.cleaner import pulisci_csv_big_ambitions
from utils.analyzer import estrai_business_da_revenue
from utils.visualizer import crea_revenue_trend
from utils.visualizer import crea_wage_trend






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
            
             # Trend wages
            st.subheader("💰 Wage Cost Analysis")
            
            # Checkbox per switch business - day
            per_day = st.checkbox("Aggrega per giorno", value=False)
            # Trend wages
            fig_wages = crea_wage_trend(df)
            st.plotly_chart(fig_wages, use_container_width=True)
else:
    st.info("👆 Carica un file CSV per iniziare l'analisi")