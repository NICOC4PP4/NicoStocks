import os
import requests
import time
import yfinance as yf
from typing import Optional, Dict, List

FMP_API_KEY = os.getenv("FMP_API_KEY")

class DataManager:
    def __init__(self):
        self.session = requests.Session()
    
    def _get_fmp(self, endpoint: str, params: dict = {}) -> Optional[dict]:
        """Realiza requests a FMP con retry logic."""
        url = f"https://financialmodelingprep.com/api/v3/{endpoint}"
        params["apikey"] = FMP_API_KEY
        
        for attempt in range(3):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data: return None
                return data
            except requests.RequestException as e:
                if response.status_code == 403:
                    print(f"FMP Permission Error (Free Tier?): {endpoint}. Skipping.")
                    return None
                print(f"Error fetching {endpoint}: {e}. Retrying ({attempt+1}/3)...")
                time.sleep(2 ** attempt)
        return None

    def get_pe_ntm(self, ticker: str) -> Optional[float]:
        """Calcula PE NTM sumando EPS estimados de los próximos 4 trimestres."""
        data = self._get_fmp(f"analyst-estimates/{ticker}", {"period": "quarter", "limit": 6})
        if not data: return None
        
        # Filtrar fechas futuras y tomar las próximas 4
        # Nota: Simplificación. En prod validar fechas contra hoy.
        future_eps = [x['estimatedEpsAvg'] for x in data[:4]]
        total_eps_ntm = sum(future_eps)
        
        price = self.get_current_price(ticker)
        if total_eps_ntm > 0 and price:
            return round(price / total_eps_ntm, 2)
        return None

    def get_fcf_per_share(self, ticker: str) -> Optional[float]:
        """Calcula FCF/Share = (OCF - Capex) / SharesOutstanding."""
        cf_data = self._get_fmp(f"cash-flow-statement/{ticker}", {"period": "annual", "limit": 1})
        if not cf_data: return None
        
        latest = cf_data[0]
        ocf = latest.get("netCashProvidedByOperatingActivities", 0)
        capex = latest.get("capitalExpenditure", 0)
        shares = latest.get("weightedAverageShsOutDil", 1) # Evitar div/0
        
        fcf = ocf - abs(capex) # Capex suele venir negativo o positivo según proveedor, asegurar resta.
        return round(fcf / shares, 2)

    def get_current_price(self, ticker: str) -> float:
        try:
            # Usamos yfinance para precios tiempo real (más rápido/barato)
            ticker_obj = yf.Ticker(ticker)
            # fast_info es más rápido que history
            return round(ticker_obj.fast_info['last_price'], 2)
        except Exception:
            return 0.0
