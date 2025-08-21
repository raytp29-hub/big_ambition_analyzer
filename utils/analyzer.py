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
    # TODO refactor - estrarre logica wages in analyzer
    from utils.visualizer import crea_wage_trend
    
    revenue_df = df[df["type"] == "Revenue"].copy()

    if len(revenue_df) == 0:
        return pd.DataFrame()
    
    def rimuovi_revenue(descrizione):
        parti = descrizione.split()
        if parti[-1] == "Revenue":
            return " ".join(parti[:-1])
        return descrizione
    
    revenue_df["business"] = revenue_df["description"].apply(rimuovi_revenue)
    revenue_per_business = revenue_df.groupby("business")["price"].sum()
    
    
    business_names = revenue_df["business"].unique()
    # Wage per business usando la funzione create_wage
    try:
        _, wage_data = crea_wage_trend(df, debug=True)
        wage_per_business = wage_data.groupby("business")["price"].sum()  # Rendiamo negativo
    except:
        wage_per_business = pd.Series()
        
        
        
        # Costi per marketing
    marketing_df = df[df["type"] == "Marketing"].copy()
    marketing_df["price"] = marketing_df["price"].astype(float)

    # Funzione riutilizzabile (ottima!)
    def estrai_business_generale(description, lista_business):
        for business in lista_business:
            if business in description:
                return business
        return "Non Allocato"

    # 1. Aggiungi colonna business
    marketing_df["business"] = marketing_df["description"].apply(
        lambda x: estrai_business_generale(x, business_names)
    )

    # 2. Filtra solo quelli allocati
    marketing_allocato = marketing_df[marketing_df["business"] != "Non Allocato"]

    # 3. Aggrega per business
    marketing_per_business = marketing_allocato.groupby("business")["price"].sum() * -1
    
    # Delivery contract
    delivery_df = df[df["type"] == "Delivery Contract"].copy()
    delivery_df["business"] = delivery_df["description"].apply(lambda x: estrai_business_generale(x, business_names))
    delivery_per_business = delivery_df[delivery_df["business"] != "Non Allocato"].groupby("business")["price"].sum() * -1
    # Estrarre la spesa e aggiungerli a costi generali
    
    
      # Rent
    rent_df = df[df["type"] == "Rent"].copy()
    rent_totale = rent_df["price"].sum()
      
    
    
    costi_generali = {
        "Rent": df[df["type"] == "Rent"]["price"].sum(),
        "Loan Payment": df[df["type"] == "Loan Payment"]["price"].sum(),
        "Item Purchase": df[df["type"] == "Item Purchase"]["price"].sum(),
        "Others": 0
    }
    
    
    
    
    
  
      
      
      
      
        
    # Creazione DataFrame P&L
    p_l_df = pd.DataFrame({
        "revenue": revenue_per_business,
        "wages": wage_per_business,
        "marketing": marketing_per_business,
        "delivery": delivery_per_business
    }).fillna(0)
    
    
    p_l_df["costi_diretti"] = p_l_df["wages"] + p_l_df["marketing"] + p_l_df["delivery"]
    p_l_df["margine_lordo"] = p_l_df["revenue"] + p_l_df["costi_diretti"]
    p_l_df["profit"] = p_l_df["revenue"] - p_l_df["wages"] - p_l_df["marketing"] - p_l_df["delivery"]
    
    # Resettiamo l'index per avere business come colonna 
    p_l_df = p_l_df.reset_index()
    p_l_df.rename(columns={"index": "business"}, inplace=True)
    
    
    return p_l_df, costi_generali