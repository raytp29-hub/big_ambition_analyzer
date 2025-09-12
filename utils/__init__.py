"""# Mostra preview
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
                    "item_purchase":"€{:,.2f}",
                    "rent":"€{:,.2f}",
                    "loan":"€{:,.2f}",
                    "profit":"€{:,.2f}",
                    "costi_totali":"€{:,.2f}",
                    "margine_lordo":"€{:,.2f}",
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
                st.metric("Costi Totali", f"€{p_l_df["costi_totali"].sum():,.2f}")
            with col5:
                margin = (p_l_df['profit'].sum() / p_l_df['revenue'].sum() * 100) if p_l_df['revenue'].sum() > 0 else 0
                st.metric("📊 Margine %", f"{margin:.1f}%")
        else:
            st.warning("Nessun dato disponibile per il P&L")  
            
            
            
            
            
            
            
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
                    st.info("Seleziona almeno un business per l'analisi stipendi")
            except Exception as e:
                st.error(f"Errore nell'analisi wages: {str(e)}")
            
            
            """      
