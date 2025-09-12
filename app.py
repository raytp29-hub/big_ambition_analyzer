import streamlit as st
import pandas as pd
import plotly.express as px

from utils.cleaner import pulisci_csv_big_ambitions
from utils.analyzer import estrai_business_da_revenue
from utils.visualizer import crea_revenue_trend
from utils.visualizer import crea_wage_trend
from utils.analyzer import crea_p_l
from utils.analyzer import calcola_growth_rate

st.set_page_config(
    page_title="Big Ambitions Analyzer",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Big Ambitions Business Analyzer")
st.write("Analyze your business data from Big Ambitions")


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

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💼 P&L Dettagliato", "📈 Analisi Trend", "⚙️ Impostazioni", "🎯 Analisi Avanzate"])

        # Calcolo P&L
        business_names, revenue_per_business, revenue_df = estrai_business_da_revenue(df)
        p_l_df, costi_generali = crea_p_l(df)

        with tab1:
            st.subheader("📊 Business Overview")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Righe totali", len(df))
            with col2:
                st.metric("Tipi di transazione", df["type"].nunique())
            with col3:
                st.metric("Business trovati", len(business_names))

            st.divider()

            # Metriche P&L Principali
            st.subheader("💰 Performance Finanziaria")

            # Metriche principali
            if not p_l_df.empty:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("💰 Revenue Totale", f"€{p_l_df['revenue'].sum():,.2f}")
                with col2:
                    st.metric("💸 Wages Totali", f"€{p_l_df['wages'].sum():,.2f}")
                with col3:
                    st.metric("📈 Profitto Totale", f"€{p_l_df['profit'].sum():,.2f}")
                with col4:
                    st.metric("💳 Costi Totali", f"€{p_l_df['costi_totali'].sum():,.2f}")
                with col5:
                    margin = (p_l_df['profit'].sum() / p_l_df['revenue'].sum() * 100) if p_l_df['revenue'].sum() > 0 else 0
                    st.metric("📊 Margine %", f"{margin:.1f}%")

            st.divider()

            # Grafico Principale
            st.subheader("🏢 Revenue per Business")

            if revenue_per_business is not None:
                fig = px.bar(
                    x=revenue_per_business.index,
                    y=revenue_per_business.values,
                    title="Revenue per Business",
                    labels={"x": "Business", "y": "Revenue"},
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

        with tab2:
            st.subheader("💼 Profit & Loss Dettagliato")

            if not p_l_df.empty:
                # Opzioni di visualizzazione
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("Visualizzazione dettagliata del Profit & Loss per ogni business")
                with col2:
                    show_all_columns = st.checkbox("Mostra tutte le colonne", value=True)

                # Tabella P&L
                if show_all_columns:
                    display_df = p_l_df
                else:
                    # Mostra solo colonne principali
                    display_df = p_l_df[["business", "revenue", "costi_totali", "profit"]]

                st.dataframe(
                    display_df.style.format({
                        "revenue": "€{:,.2f}",
                        "wages": "€{:,.2f}",
                        "marketing": "€{:,.2f}",
                        "delivery": "€{:,.2f}",
                        "item_purchase": "€{:,.2f}",
                        "rent": "€{:,.2f}",
                        "loan": "€{:,.2f}",
                        "profit": "€{:,.2f}",
                        "costi_totali": "€{:,.2f}",
                        "margine_lordo": "€{:,.2f}",
                    }),
                    use_container_width=True
                )

                # Bottone per export
                st.download_button(
                    label="📁 Scarica P&L come CSV",
                    data=p_l_df.to_csv(index=False),
                    file_name="business_pl.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Nessun dato disponibile per il P&L")

        with tab3:
            st.subheader("📈 Analisi Trend")

            # === REVENUE TREND ===
            st.subheader("💰 Trend Revenue per Business")

            if revenue_df is not None and not revenue_df.empty:
                # Controlli per Revenue Trend
                col1, col2 = st.columns([2, 1])
                with col1:
                    business_revenue_filter = st.multiselect(
                        "Seleziona business per il Trend Revenue:",
                        options=business_names,
                        default=business_names,
                        key="revenue_filter"
                    )
                with col2:
                    show_cumulative = st.checkbox("Vista cumulativa", value=False)

                # Grafico Revenue Trend
                if business_revenue_filter:
                    revenue_filtered = revenue_df[revenue_df['business'].isin(business_revenue_filter)]
                    fig_trend = crea_revenue_trend(revenue_filtered)
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("Seleziona almeno un business per visualizzare il trend")

            st.divider()

            # === ANALISI COSTI STIPENDI ===
            st.subheader("💸 Analisi Costi Stipendi")

            # Controlli per Wage Analysis
            col1, col2, col3 = st.columns([2, 2, 6])
            with col1:
                vista_giorno = st.checkbox("Vista per giorno", value=False)
            with col2:
                tipo_grafico = st.radio("📊 Tipo grafico", ["bar", "line"], horizontal=True)
            with col3:
                business_selezionati = st.multiselect(
                    "Filtra per business:",
                    options=business_names,
                    default=business_names,
                    key="wage_filter"
                )

            # Grafico Wage Analysis
            try:
                if business_selezionati:
                    fig_wages = crea_wage_trend(
                        df,
                        kind=tipo_grafico,
                        per_day=vista_giorno,
                        per_business=business_selezionati
                    )
                    st.plotly_chart(fig_wages, use_container_width=True)
                else:
                    st.info("Seleziona almeno un business per l'analisi degli stipendi")
            except Exception as e:
                st.error(f"Errore nell'analisi dei salari: {str(e)}")

        with tab4:
            st.subheader("⚙️ Impostazioni e Dati")

            # === PREVIEW DATI ===
            with st.expander("📊 Anteprima dati puliti", expanded=False):
                st.write(f"Dataset con {len(df)} righe e {len(df.columns)} colonne")

                # Selezione righe da mostrare
                num_rows = st.slider("Numero di righe da visualizzare:", 5, 50, 10)
                st.dataframe(df.head(num_rows), use_container_width=True)

            # === INFO DATASET ===
            with st.expander("ℹ️ Informazioni sul Dataset", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Tipi di transazione:**")
                    type_counts = df['type'].value_counts()
                    st.dataframe(type_counts.to_frame('Conteggio'))

                with col2:
                    st.write("**Periodo analizzato:**")
                    if 'day' in df.columns:
                        st.metric("Giorno minimo", df['day'].min())
                        st.metric("Giorno massimo", df['day'].max())
                        st.metric("Giorni totali", df['day'].nunique())

            # === EXPORT ===
            with st.expander("📁 Esportazione Dati", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="📄 Scarica dati puliti (CSV)",
                        data=df.to_csv(index=False),
                        file_name="big_ambitions_cleaned.csv",
                        mime="text/csv"
                    )

                with col2:
                    if not p_l_df.empty:
                        st.download_button(
                            label="💼 Scarica P&L (CSV)",
                            data=p_l_df.to_csv(index=False),
                            file_name="profit_loss_analysis.csv",
                            mime="text/csv"
                        )

            # === CONFIGURAZIONI ===
            with st.expander("🔧 Configurazioni Avanzate", expanded=False):
                st.info("Questa sezione può essere espansa per future funzionalità come:")
                st.write("• Impostazione valuta personalizzata")
                st.write("• Configurazione soglie di categorizzazione")
                st.write("• Filtri temporali avanzati")
                st.write("• Esportazione in formati multipli")

        with tab5:
            st.subheader("🎯 Analisi Avanzate")

            # === BREAK-EVEN ANALYSIS ===
            st.subheader("💰 Analisi del Punto di Pareggio (Break-Even)")
            
            

            if not p_l_df.empty:
                break_even_df = p_l_df[["business", "revenue", "costi_totali", "profit"]].copy()
                break_even_df["gap_break_even_status"] = break_even_df["profit"].apply(
                    lambda x: "✅ Profittevole" if x > 0 else "❌ In Perdita"
                )
                break_even_df["margine_di_sicurezza"] = break_even_df["profit"] / break_even_df["revenue"] * 100
                break_even_df["gap_break_even"] = break_even_df["profit"].apply(
                    lambda x: abs(x) if x < 0 else 0
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(
                        break_even_df.style.format({
                            "revenue": "€{:,.2f}",
                            "costi_totali": "€{:,.2f}",
                            'profit': '€{:,.2f}',
                            'margine_di_sicurezza': '{:.1f}%',
                            'gap_break_even': '€{:,.2f}'
                        }),
                        use_container_width=True
                    )

                with col2:
                    profitable_count = (break_even_df["profit"] > 0).sum()
                    st.metric("Business profittevoli", f"{profitable_count}/{len(break_even_df)}")

                    avg_margin = break_even_df["margine_di_sicurezza"].mean()
                    st.metric("Margine medio", f"{avg_margin:.1f}%")

            st.divider()

            # === TREND DI CRESCITA ===
            st.subheader("📈 Trend di Crescita")

            # Controlli per vista temporale
            col1, col2, col3 = st.columns([2, 2, 4])
            with col1:
                vista_temporale = st.radio(
                    "Vista temporale:",
                    ["Giornaliera", "Settimanale", "Cumulativa"],
                    horizontal=True
                )
            with col2:
                metrica_crescita = st.selectbox(
                    "Metrica da analizzare:",
                    ["Revenue", "Profit", "Costi"]
                )
            with col3:
                business_crescita = st.multiselect(
                    "Business da confrontare:",
                    options=business_names,
                    default=business_names,
                    key="growth_filter"
                )

            # Mapping delle opzioni UI ai valori della funzione
            metrica_map = {
                "Revenue": "revenue",
                "Profit": "profit",
                "Costi": "costi"
            }

            vista_map = {
                "Giornaliera": "day-over-day",
                "Settimanale": "settimanale",
                "Cumulativa": "cumulativo"
            }

            # === CALCOLO E VISUALIZZAZIONE GROWTH ===
            if business_crescita and metrica_crescita == "Revenue":
                try:
                    growth_df = calcola_growth_rate(
                        df,
                        metrica=metrica_map[metrica_crescita],
                        vista=vista_map[vista_temporale],
                        business_filter=business_crescita
                    )

                    if not growth_df.empty:
                        st.subheader(f"Growth Rate - {metrica_crescita} ({vista_temporale})")

                        # Mostra tabella
                        st.dataframe(
                            growth_df.style.format({
                                "price": "€{:,.2f}",
                                "growth_rate": "{:.2f}%",
                                "previous_value": "€{:,.2f}"
                            }),
                            use_container_width=True
                        )
                        
                        if not growth_df.empty:
                            st.subheader(f"Growth Rate - {metrica_crescita} ({vista_temporale})")

                        # Grafico semplice
                        if len(growth_df) > 1:
                            fig = px.line(
                                growth_df,
                                x="day",
                                y="growth_rate",
                                color="business",
                                title=f"Growth Rate % - {metrica_crescita} ({vista_temporale})"
                            )
                            st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.warning("Nessun dato disponibile per la crescita")

                except Exception as e:
                    st.error(f"Errore nel calcolo della crescita: {str(e)}")
            else:
                st.info("Seleziona almeno un business e scegli 'Revenue' per vedere i trend di crescita")

else:
    st.info("👆 Carica un file CSV per iniziare l'analisi")