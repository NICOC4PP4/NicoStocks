import reflex as rx
import os
from supabase import create_client, Client
from utils.data_engine import DataManager
from utils.finance_core import calculate_twr
import pandas as pd

# Supabase Init
# Supabase Init
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY missing. Client not initialized.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

class State(rx.State):
    """Estado global de la aplicación."""
    
    # Portfolio Data
    holdings: list[dict] = []
    total_value: float = 0.0
    twr_metric: float = 0.0
    benchmark_data: list[dict] = [] # Para gráfico
    
    # Watchlist Data
    watchlist: list[dict] = []
    
    def load_data(self):
        """Carga inicial de datos."""
        self.fetch_portfolio()
        self.fetch_watchlist()
    
    def fetch_portfolio(self):
        # 1. Obtener Transacciones
        response = supabase.table("transactions").select("*").execute()
        trans_df = pd.DataFrame(response.data)
        
        if trans_df.empty: return

        # 2. Agrupar por Ticker para ver tenencias actuales
        # (Lógica simplificada, asume solo compras)
        holdings_grp = trans_df.groupby('ticker')['shares'].sum().reset_index()
        
        dm = DataManager()
        current_holdings = []
        current_total = 0.0
        
        for index, row in holdings_grp.iterrows():
            ticker = row['ticker']
            shares = row['shares']
            
            # Obtener fundamentales de DB o API (simplificado API directa aquí)
            price = dm.get_current_price(ticker)
            pe = dm.get_pe_ntm(ticker) or 0
            fcf = dm.get_fcf_per_share(ticker) or 0
            
            val = shares * price
            current_total += val
            
            current_holdings.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": val,
                "pe_ntm": pe,
                "fcf_share": fcf
            })
            
        self.holdings = current_holdings
        self.total_value = round(current_total, 2)
        
        # Calcular TWR
        self.twr_metric = calculate_twr(trans_df, self.total_value)

    def fetch_watchlist(self):
        # Mockup data or DB fetch
        pass
