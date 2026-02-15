import os
import requests
import time
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List

FMP_API_KEY = os.getenv("FMP_API_KEY")


class DataManager:
    def __init__(self):
        self.session = requests.Session()

    def _get_fmp(self, endpoint: str, params: dict = None) -> Optional[list | dict]:
        """Realiza requests a FMP con retry logic."""
        if params is None:
            params = {}
        url = f"https://financialmodelingprep.com/api/v3/{endpoint}"
        params["apikey"] = FMP_API_KEY

        response = None
        for attempt in range(3):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data:
                    return None
                return data
            except requests.RequestException as e:
                if response is not None and response.status_code == 403:
                    print(f"FMP Permission Error (Free Tier?): {endpoint}. Skipping.")
                    return None
                print(f"Error fetching {endpoint}: {e}. Retrying ({attempt + 1}/3)...")
                time.sleep(2 ** attempt)
        return None

    # ── Validación de Ticker ──────────────────────────────────────────

    def validate_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Verifica que un ticker exista en FMP.
        Retorna dict con name, sector, description si existe; None si no.
        """
        data = self._get_fmp(f"profile/{ticker}")
        if not data:
            return None
        profile = data[0] if isinstance(data, list) else data
        return {
            "name": profile.get("companyName", ticker),
            "sector": profile.get("sector", "Unknown"),
            "description": (profile.get("description", "") or "")[:500],
        }

    # ── Earnings Calendar ─────────────────────────────────────────────

    def get_earnings_calendar(self, tickers: List[str], days: int = 7) -> List[Dict]:
        """
        Consulta el calendario de earnings de FMP.
        Retorna earnings dentro de los próximos `days` días para los tickers dados.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        data = self._get_fmp("earning_calendar", {"from": today, "to": future})
        if not data:
            return []

        tickers_upper = {t.upper() for t in tickers}
        return [
            {
                "ticker": item["symbol"],
                "date": item["date"],
                "eps_estimated": item.get("epsEstimated"),
                "revenue_estimated": item.get("revenueEstimated"),
            }
            for item in data
            if item.get("symbol", "").upper() in tickers_upper
        ]

    # ── Cambio de Precio Diario ───────────────────────────────────────

    def get_daily_price_change(self, ticker: str) -> Optional[float]:
        """Retorna el % de cambio del día usando yfinance."""
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) < 2:
                return None
            prev_close = hist["Close"].iloc[-2]
            current = hist["Close"].iloc[-1]
            if prev_close == 0:
                return None
            return round(((current - prev_close) / prev_close) * 100, 2)
        except Exception:
            return None

    # ── Fundamentales ─────────────────────────────────────────────────

    def get_pe_ntm(self, ticker: str) -> Optional[float]:
        """Calcula PE NTM sumando EPS estimados de los próximos 4 trimestres."""
        data = self._get_fmp(f"analyst-estimates/{ticker}", {"period": "quarter", "limit": 6})
        if not data:
            return None

        future_eps = [x.get("estimatedEpsAvg", 0) for x in data[:4]]
        total_eps_ntm = sum(future_eps)

        price = self.get_current_price(ticker)
        if total_eps_ntm > 0 and price:
            return round(price / total_eps_ntm, 2)
        return None

    def get_fcf_per_share(self, ticker: str) -> Optional[float]:
        """Calcula FCF/Share = (OCF - Capex) / SharesOutstanding."""
        cf_data = self._get_fmp(f"cash-flow-statement/{ticker}", {"period": "annual", "limit": 1})
        if not cf_data:
            return None

        latest = cf_data[0]
        ocf = latest.get("netCashProvidedByOperatingActivities", 0)
        capex = latest.get("capitalExpenditure", 0)
        shares = latest.get("weightedAverageShsOutDil", 1)

        fcf = ocf - abs(capex)
        return round(fcf / shares, 2)

    def get_current_price(self, ticker: str) -> float:
        """Obtiene precio actual via yfinance."""
        try:
            ticker_obj = yf.Ticker(ticker)
            return round(ticker_obj.fast_info["last_price"], 2)
        except Exception:
            return 0.0
