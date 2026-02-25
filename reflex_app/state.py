import reflex as rx
import os
from supabase import create_client, Client
from utils.data_engine import DataManager
from utils.finance_core import calculate_twr
import pandas as pd
from datetime import datetime
import yfinance as yf

# ── Supabase Init ─────────────────────────────────────────────────────
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY missing. Client not initialized.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

dm = DataManager()


from pydantic import BaseModel

class Holding(BaseModel):
    """Typed data model for portfolio holdings."""
    ticker: str = ""
    shares: float = 0.0
    avg_buy: float = 0.0
    price: float = 0.0
    value: float = 0.0
    pnl_pct: float = 0.0
    pe_ntm: float = 0.0
    fcf_share: float = 0.0

class RecentActivity(BaseModel):
    """Typed data model for recent transactions."""
    ticker: str = ""
    action: str = ""
    qty: str = ""
    price: str = ""
    date: str = ""

class WatchlistItem(BaseModel):
    """Typed data model for watchlist items."""
    ticker: str = ""
    price: float = 0.0
    change_pct: float = 0.0
    market_cap: str = ""
    pe_ntm: float = 0.0


class State(rx.State):
    """Estado global de la aplicación SmartFolio."""

    # ── Portfolio Data ────────────────────────────────────────────────
    holdings: list[Holding] = []
    total_value: float = 0.0
    total_pnl: float = 0.0
    twr_metric: float = 0.0
    benchmark_data: list[dict] = []
    
    # ── Search & Filters ─────────────────────────────────────────────
    search_ticker: str = ""

    @rx.var
    def filtered_holdings(self) -> list[Holding]:
        """Retorna holdings filtrados por el ticker ingresado en el buscador."""
        search = self.search_ticker.strip().upper()
        if not search:
            return self.holdings
        return [h for h in self.holdings if search in h.ticker.upper()]

    # ── Dashboard Data ────────────────────────────────────────────────
    total_portfolio_value: float = 0.0
    daily_pnl: float = 0.0
    daily_pnl_percent: float = 0.0
    recent_activity: list[RecentActivity] = []

    # ── Watchlist Data ────────────────────────────────────────────────
    watchlist: list[WatchlistItem] = []

    # ── Transaction Form ──────────────────────────────────────────────
    show_modal: bool = False
    form_ticker: str = ""
    form_date: str = ""
    form_shares: str = ""
    form_price: str = ""
    form_error: str = ""
    form_loading: bool = False

    # ── Modal Controls ────────────────────────────────────────────────

    def toggle_modal(self, open: bool):
        """Sincroniza el estado del modal con el componente."""
        self.show_modal = open
        if open:
            self.form_ticker = ""
            self.form_date = datetime.now().strftime("%Y-%m-%d")
            self.form_shares = ""
            self.form_price = ""
            self.form_error = ""

    def open_modal(self):
        """Abre el modal."""
        self.toggle_modal(True)

    def close_modal(self):
        """Cierra el modal."""
        self.toggle_modal(False)

    # ── Core: Agregar Transacción ─────────────────────────────────────

    def add_transaction(self):
        """
        1. Valida campos del formulario
        2. Verifica ticker con FMP
        3. Auto-registra asset si es nuevo
        4. Inserta transacción en Supabase
        5. Recalcula portfolio
        """
        if not supabase:
            self.form_error = "Database not connected."
            return

        # ── Validación de campos ──
        ticker = self.form_ticker.strip().upper()
        if not ticker:
            self.form_error = "Ticker is required."
            return

        try:
            shares = float(self.form_shares)
            price = float(self.form_price)
            if shares <= 0 or price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self.form_error = "Shares and Price must be positive numbers."
            return

        if not self.form_date:
            self.form_error = "Date is required."
            return

        self.form_loading = True
        self.form_error = ""

        # ── Verificar Ticker con FMP ──
        profile = dm.validate_ticker(ticker)
        if not profile:
            self.form_error = f"Ticker '{ticker}' not found in FMP."
            self.form_loading = False
            return

        # ── Auto-registrar Asset si es nuevo ──
        existing = supabase.table("assets").select("ticker").eq("ticker", ticker).execute()
        if not existing.data:
            supabase.table("assets").insert({
                "ticker": ticker,
                "name": profile["name"],
                "sector": profile["sector"],
                "description": profile.get("description", ""),
            }).execute()

        # ── Insertar Transacción ──
        supabase.table("transactions").insert({
            "ticker": ticker,
            "date": self.form_date,
            "type": "BUY",
            "shares": shares,
            "price": price,
        }).execute()

        # ── Limpiar y recargar ──
        self.form_loading = False
        self.show_modal = False
        self.fetch_portfolio()
        self.fetch_dashboard_data()

    # ── Core: Cargar Portfolio ────────────────────────────────────────

    def load_data(self):
        """Carga inicial de datos."""
        self.fetch_portfolio()
        self.fetch_dashboard_data()
        self.fetch_watchlist()

    def fetch_dashboard_data(self):
        """Calcula KPIs del Dashboard y obtiene actividad reciente."""
        if not supabase:
            return

        # ── Obtener últimas 5 transacciones ──
        response = supabase.table("transactions").select("*").order("date", desc=True).limit(5).execute()
        
        self.recent_activity = []
        for tx in response.data:
            self.recent_activity.append(RecentActivity(
                ticker=tx["ticker"],
                action=tx["type"],
                qty=f"{tx['shares']} Shares",
                price=f"${tx['price']:.2f}",
                date=self._format_date(tx["date"]),
            ))

        # ── Calcular Portfolio Value y Daily P&L ──
        response = supabase.table("transactions").select("*").execute()
        trans_df = pd.DataFrame(response.data)

        if trans_df.empty:
            self.total_portfolio_value = 0.0
            self.daily_pnl = 0.0
            self.daily_pnl_percent = 0.0
            return

        # Agrupar por Ticker para obtener posiciones actuales
        grouped = trans_df.groupby("ticker").agg(
            total_shares=("shares", "sum"),
        ).reset_index()

        current_total = 0.0
        yesterday_total = 0.0

        for _, row in grouped.iterrows():
            ticker = row["ticker"]
            shares = float(row["total_shares"])

            if shares <= 0:
                continue

            # Obtener precio actual y anterior usando yfinance
            try:
                t = yf.Ticker(ticker)
                current_price = t.fast_info.get("last_price", 0)
                previous_close = t.fast_info.get("previous_close", 0)
                
                current_total += shares * current_price
                yesterday_total += shares * previous_close
            except Exception as e:
                print(f"Error fetching prices for {ticker}: {e}")
                continue

        self.total_portfolio_value = round(current_total, 2)
        self.daily_pnl = round(current_total - yesterday_total, 2)
        self.daily_pnl_percent = (
            round((self.daily_pnl / yesterday_total) * 100, 2)
            if yesterday_total > 0
            else 0.0
        )

    def _format_date(self, date_str: str) -> str:
        """Formatea fecha para mostrar 'Today', 'Yesterday' o fecha."""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = (today - date).days
            
            if delta == 0:
                return "Today"
            elif delta == 1:
                return "Yesterday"
            else:
                return date.strftime("%b %d")
        except:
            return date_str

    def fetch_portfolio(self):
        """Obtiene transacciones y calcula holdings con PnL."""
        if not supabase:
            return

        response = supabase.table("transactions").select("*").execute()
        trans_df = pd.DataFrame(response.data)

        if trans_df.empty:
            self.holdings = []
            self.total_value = 0.0
            self.total_pnl = 0.0
            return

        # Agrupar por Ticker
        grouped = trans_df.groupby("ticker").agg(
            total_shares=("shares", "sum"),
            total_cost=("amount", "sum"),
        ).reset_index()

        current_holdings = []
        current_total = 0.0
        total_cost_all = 0.0

        for _, row in grouped.iterrows():
            ticker = row["ticker"]
            shares = float(row["total_shares"])
            total_cost = float(row["total_cost"])

            if shares <= 0:
                continue

            avg_buy = round(total_cost / shares, 2)
            price = dm.get_current_price(ticker)
            value = round(shares * price, 2)
            pnl_pct = round(((price - avg_buy) / avg_buy) * 100, 2) if avg_buy > 0 else 0.0

            current_total += value
            total_cost_all += total_cost

            current_holdings.append(Holding(
                ticker=ticker,
                shares=round(shares, 4),
                avg_buy=avg_buy,
                price=price,
                value=value,
                pnl_pct=pnl_pct,
                pe_ntm=dm.get_pe_ntm(ticker) or 0,
                fcf_share=dm.get_fcf_per_share(ticker) or 0,
            ))

        self.holdings = current_holdings
        self.total_value = round(current_total, 2)
        self.total_pnl = (
            round(((current_total - total_cost_all) / total_cost_all) * 100, 2)
            if total_cost_all > 0
            else 0.0
        )
        self.twr_metric = calculate_twr(trans_df, self.total_value)

    def fetch_watchlist(self):
        """Obtiene la lista de seguimiento y sus precios actuales."""
        if not supabase:
            return

        response = supabase.table("watchlist").select("ticker").execute()
        tickers = [item["ticker"] for item in response.data]

        self.watchlist = []
        for ticker in tickers:
            try:
                price = dm.get_current_price(ticker)
                # Estimamos cambio diario y market cap (mock o simple info)
                t = yf.Ticker(ticker)
                change_pct = round(t.fast_info.get("day_change_percent", 0) * 100, 2)
                mcap = t.fast_info.get("market_cap", 0)
                mcap_str = f"${mcap/1e9:.1f}B" if mcap > 1e9 else f"${mcap/1e6:.1f}M"
                
                self.watchlist.append(WatchlistItem(
                    ticker=ticker,
                    price=price,
                    change_pct=change_pct,
                    market_cap=mcap_str,
                    pe_ntm=dm.get_pe_ntm(ticker) or 0
                ))
            except Exception as e:
                print(f"Error fetching watchlist for {ticker}: {e}")

    def toggle_watchlist(self, ticker: str):
        """Agrega o quita un ticker de la watchlist."""
        if not supabase:
            return

        ticker = ticker.upper()
        existing = [w.ticker for w in self.watchlist]
        
        if ticker in existing:
            supabase.table("watchlist").delete().eq("ticker", ticker).execute()
        else:
            # Primero asegurar que existe en assets
            profile = dm.validate_ticker(ticker)
            if profile:
                supabase.table("assets").insert({
                    "ticker": ticker,
                    "name": profile["name"],
                    "sector": profile["sector"],
                }).upsert().execute()
                
                supabase.table("watchlist").insert({"ticker": ticker}).execute()

        self.fetch_watchlist()
