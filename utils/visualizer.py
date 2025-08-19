import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st




def crea_revenue_trend(df):
    revenue_per_day = df.groupby(["business","day"])["price"].sum().reset_index().sort_values(["day","business"], ascending=[True,True])
    
    
    # Creazione del grafico
    fig = px.line(
        revenue_per_day,
        x="day",
        y="price",
        labels={'day': 'Giorno', 'price': 'Revenue'},
        color="business",
        title="Revenue Trend per Business"
    )
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(title='Giorno', dtick=1)
    fig.update_yaxes(tickformat=",.")
    fig.update_layout(
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig





def crea_wage_trend(df):
   
   
    # Aggiungere la funzione per pulire il salario dalla descrizione
    def rimuovi_des_salario(salario):
        parti = salario.split("(")
        return parti[1].replace(" Daily Wage)", "")
    
    costi_wage = df[df["type"] == "Wage"].copy()
    st.write("Costi Wage", costi_wage.head())
    costi_wage.loc[:, "price"] = costi_wage["price"].astype(float)

    costi_wage["business"] = costi_wage["description"].apply(rimuovi_des_salario)
    costi_wages_per_business = (costi_wage.groupby("business")["price"].sum().reset_index())
    st.write("Dati per Business", costi_wages_per_business)
    
   
   # Creazione del grafico
    fig = px.line(
        costi_wages_per_business,
        x="business",
        y="price",
        color="price",
        title="Revenue Trend per Business"
    )
    
    return fig

