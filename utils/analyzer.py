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

# Da implementare?
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
        _, wage_data = crea_wage_trend(df, debug=False)
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
    rent_totale = rent_df["price"].sum() * -1 
      
    
    
    costi_generali = {
        "Rent": df[df["type"] == "Rent"]["price"].sum(),
        "Loan Payment": df[df["type"] == "Loan Payment"]["price"].sum(),
        "Item Purchase": df[df["type"] == "Item Purchase"]["price"].sum(),
        "Others": 0
    }
    
    
    
    
    # Categorizzazione dei negozi per business e personale
    
    def category_purchase_for_business(desc):
        if desc.startswith("Purchase from "):
            return desc.replace("Purchase from ", "")
        return desc
    
        
    def categorizza_negozio(nome_negozio):
        b_to_b = ["NY Distro Inc", "AJ Pederson & Son", "Square Appliances", "Essentials Appliances", "IKA BOHAG"]
        
        negozi_personali = ["Donut Days", "Slider Shack", "Joe's Hotdogs", "United Gasoline"]
        
        
        if nome_negozio in b_to_b:
            return "business"
        elif nome_negozio in negozi_personali:
            return "personale"
        else:
            return "altro"
        
        
        

    item_purchase_df = df[df["type"] == "Item Purchase"].copy()
    item_purchase_df["business_name"] = item_purchase_df["description"].apply(category_purchase_for_business)
    item_purchase_df["category"] = item_purchase_df["business_name"].apply(categorizza_negozio)
    
    
    item_business = item_purchase_df[item_purchase_df["category"] == "business"]
    items_personal = item_purchase_df[item_purchase_df["category"] == "peronale"]
    item_others = item_purchase_df[item_purchase_df["category"] == "altro"]
    
    
    totale_item_business = item_business["price"].sum() * -1 
    
    
    num_business = len(business_names)
    costo_per_business = totale_item_business / num_business
      
    # Rent
    costo_rent_per_business = rent_totale / num_business  
    
    
    
    # Loan 
    loan_df = df[df["type"] == "Loan Payment"].copy()
    totale_loan = loan_df["price"].sum() * -1
    costo_loan_per_business = totale_loan / num_business
      
        
    # Creazione DataFrame P&L
    p_l_df = pd.DataFrame({
        "revenue": revenue_per_business,
        "wages": wage_per_business,
        "marketing": marketing_per_business,
        "delivery": delivery_per_business
    }).fillna(0).infer_objects(copy=False)
    
    
    
    
    p_l_df["item_purchase"] = costo_per_business
    p_l_df["rent"] = costo_rent_per_business
    p_l_df["loan"] = costo_loan_per_business
    p_l_df["costi_totali"] = p_l_df["wages"] + p_l_df["marketing"] + p_l_df["delivery"] + p_l_df["item_purchase"] + p_l_df["loan"]
    p_l_df["margine_lordo"] = p_l_df["revenue"] + p_l_df["costi_totali"]
    p_l_df["profit"] = p_l_df["revenue"] - p_l_df["costi_totali"]

    
    
    # Resettiamo l'index per avere business come colonna 
    p_l_df = p_l_df.reset_index()
    p_l_df.rename(columns={"index": "business"}, inplace=True)
    
    
    return p_l_df, costi_generali



# Implementazione analisi costi avanzati

def calcola_growth_rate(df, metrica="revenue", vista="day-over-day", business_filter=None):
    # Calcola day-over-day, settimanale, cumulativo
    if metrica == "revenue":
        revenue_df = df[df["type"] == "Revenue"].copy()
        
        # Estrarre business name dalla descrizione
        def rimuovi_revenue(descrizione):
            parti = descrizione.split()
            if parti[-1] == "Revenue":
                return " ".join(parti[:-1])
            return descrizione
        
        revenue_df["business"] = revenue_df["description"].apply(rimuovi_revenue)
        revenue_df = revenue_df.groupby(["business", "day"])["price"].sum().reset_index()
        
        
        # 3. Filtra business se specificato
        if business_filter:
            revenue_df = revenue_df[revenue_df["business"].isin(business_filter)]
        
        # 4. Aggrega per business + day
        if vista == "day-over-day":
            revenue_aggregated = revenue_df
        elif vista == "settimanale":
            # Aggrega per settimana (giorno // 7)
            revenue_df["week"] = revenue_df["day"] // 7
            revenue_aggregated = revenue_df.groupby(["business", "week"])["price"].sum().reset_index()
            revenue_aggregated.rename(columns={"week": "day"}, inplace=True)  # Per uniformità
        elif vista == "cumulativo":
            # Prima aggrega per day, poi calcola cumulativo
            daily_agg = revenue_df.groupby(["business", "day"])["price"].sum().reset_index()
            
            growth_data = []
            for business in daily_agg["business"].unique():
                business_data = daily_agg[daily_agg["business"] == business].sort_values("day")
                business_data["price"] = business_data["price"].cumsum()  # Cumulativo
                growth_data.append(business_data)
            
            revenue_aggregated = pd.concat(growth_data, ignore_index=True)
        
        # 5. Calcola growth rate per ogni business
        growth_data = []
        
        for business in revenue_aggregated["business"].unique():
            business_data = revenue_aggregated[revenue_aggregated["business"] == business].sort_values("day").copy()
            
            # Calcola growth rate (% change rispetto al periodo precedente)
            business_data["growth_rate"] = business_data["price"].pct_change() * 100
            business_data["previous_value"] = business_data["price"].shift(1)
            
            growth_data.append(business_data)
            
            # 6. Combina tutto
            final_df = pd.concat(growth_data, ignore_index=True)
            
        return final_df
    
    else:
        # Per ora placeholder per profit/costi
        return pd.DataFrame()
    
    
def calcola_proiezioni(df, business_names, giorni_futuri=14, finestra=14):
    # Proiezioni basate sui trend
    revenue_df = df[df["type"] == "Revenue"].copy()
    
    def rimuovi_revenue(descrizione):
            parti = descrizione.split()
            if parti[-1] == "Revenue":
                return " ".join(parti[:-1])
            return descrizione
        
    revenue_df["business"] = revenue_df["description"].apply(rimuovi_revenue)
    
    revenue_aggregated = revenue_df.groupby(["business","day"])["price"].sum().reset_index()
    
    for business in revenue_aggregated["business"].unique():
        business_data = revenue_aggregated[revenue_aggregated["business"] == business].sort_values("day")
        ultimi_giorni = business_data.tail(finestra)
        
        