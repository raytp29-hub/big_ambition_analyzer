from doctest import debug
import numpy as np
import pandas as pd
import plotly.express as px
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





def crea_wage_trend(df, kind="bar", per_day=False, per_business=None, debug=False):

    if df is None:
        raise ValueError("df non può essere None")

    df = df.copy()

    # normalizza type e filtra robustamente (case-insensitive)
    if "type" not in df.columns or "price" not in df.columns:
        raise ValueError("Il DataFrame deve contenere le colonne 'type' e 'price'")

    df["type"] = df["type"].astype(str).str.strip().str.lower()
    wage_df = df[df["type"].str.contains("wage", na=False)].copy()

    if debug:
        st.write("Wage rows (prime 10):")
        st.dataframe(wage_df.head(10))

    # converti price in numerico
    def to_num(x):
        if pd.isna(x):
            return np.nan
        s = str(x).strip().replace(" ", "")
        if "." in s and "," in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            s = s.replace(",", ".")
        try:
            return float(s)
        except:
            return np.nan

    wage_df["price"] = wage_df["price"].apply(to_num)

    # estrai business
    def estrai_business_from_description(s):
        if pd.isna(s):
            return "Unknown"
        s = str(s)
        if "(" in s and ")" in s:
            try:
                mid = s.split("(", 1)[1].split(")", 1)[0]
                mid = mid.replace("Daily Wage", "").replace("Daily Wage", "").strip()
                return mid or "Unknown"
            except Exception:
                return s.strip() or "Unknown"
        return s.strip() or "Unknown"
    


    if "business" not in wage_df.columns or wage_df["business"].isna().all() or (wage_df["business"].astype(str).str.strip() == "").all():
        wage_df["business"] = wage_df["description"].apply(estrai_business_from_description)
    else:
        wage_df["business"] = wage_df["business"].astype(str).str.strip()
        mask_empty = wage_df["business"].isna() | (wage_df["business"].str.len() == 0)
        if mask_empty.any():
            wage_df.loc[mask_empty, "business"] = wage_df.loc[mask_empty, "description"].apply(estrai_business_from_description)

    # filtro per business
    if per_business:
        if isinstance(per_business, str):
            per_business = [per_business]
        wage_df = wage_df[wage_df["business"].isin(per_business)]

    # aggregazione dinamica
    group_cols = ["business"]
    if per_day and "day" in wage_df.columns:
        group_cols.append("day")

    agg = wage_df.dropna(subset=["price"]).groupby(group_cols, dropna=False)["price"].sum().reset_index()

    if agg.empty:
        fig = px.scatter(x=[0], y=[0])
        fig.update_layout(
            title="Wage Cost — Nessun dato valido",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "Nessun dato Wage valido",
                "xref": "paper","yref": "paper","showarrow": False,"font": {"size": 14}
            }]
        )
        return (fig, agg) if debug else fig

    agg["price"] = agg["price"].abs()
    agg = agg.sort_values("price", ascending=False)

    # costruzione grafico
    if kind == "bar":
        if per_day and "day" in agg.columns:
            fig = px.bar(agg, x="day", y="price", color="business", title="Wage Cost per Day/Business",
                         labels={"price":"Costo Wage", "day":"Giorno"})
        else:
            fig = px.bar(agg, x="business", y="price", title="Wage Cost per Business", labels={"price":"Costo Wage"})
    else:
        if per_day and "day" in agg.columns:
            fig = px.line(agg, x="day", y="price", color="business", title="Wage Cost per Day/Business")
        else:
            fig = px.line(agg, x="business", y="price", title="Wage Cost per Business")
        fig.update_traces(mode="lines+markers")

    fig.update_layout(xaxis_title="Business/Giorno", yaxis_title="Costo Wage", height=450, hovermode="x unified")

    return (fig, agg) if debug else fig





# Implementazione visualizzazione analisi avanzate 


def crea_growth_trend_chart(growth_data, metrica, vista):
    # Grafici per growth trends
    pass
    
def crea_projection_chart(projections_data):
    # Grafici per proiezioni future
    pass
