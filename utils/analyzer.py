import pandas as pd

def estrai_business_da_revenue(df):
    # Estraiamo business name dal ravenue
    
    revenue_df = df[df["type"] == "Revenue"].copy()
    
    if len(revenue_df) == 0:
        return []
    
    def rimuovi_revenue(descrizione):
        parti = descrizione.split()
        if parti[-1] == "Revenue":
            return " ".join(parti[:-1])
        return descrizione
    
    revenue_df["business"] = revenue_df["description"].apply(rimuovi_revenue)
    
    
    revenue_per_business = revenue_df.groupby("business")["price"].sum()
    business_names = revenue_df["business"].unique().tolist()
    
    
    return business_names, revenue_per_business, revenue_df


def analizza_costi(df):
    pass


def crea_p_l(df):
    pass