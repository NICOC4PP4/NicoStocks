import reflex as rx
import os
from supabase import create_client, Client
from utils.data_engine import DataManager
from utils.finance_core import calculate_twr
import pandas as pd
from datetime import datetime

# ── Supabase Init ─────────────────────────────────────────────────────
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY missing. Client not initialized.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

dm = DataManager()


class State(rx.State):
    """Estado global de la aplicación SmartFolio."""

    # ── Portfolio Data ────────────────────────────────────────────────
    holdings: list[dict] = []
    total_value: float = 0.0
    total_pnl: float = 0.0
    twr_metric: float = 0.0
    benchmark_data: list[dict] = []

    # ── Watchlist Data ────────────────────────────────────────────────
    watchlist: list[dict] = []

    # ── Transaction Form ──────────────────────────────────────────────
    show_modal: bool = False
    form_ticker: str = ""
    form_date: str = ""
    form_shares: str = ""
    form_price: str = ""
    form_error: str = ""
    form_loading: bool = False

    # ── Modal Controls ────────────────────────────────────────────────

    def open_modal(self):
        """Abre el modal y resetea el formulario."""
        self.show_modal = True
        self.form_ticker = ""
        self.form_date = datetime.now().strftime("%Y-%m-%d")
        self.form_shares = ""
        self.form_price = ""
        self.form_error = ""

    def close_modal(self):
        self.show_modal = False
        self.form_error = ""

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

    # ── Core: Cargar Portfolio ────────────────────────────────────────

    def load_data(self):
        """Carga inicial de datos."""
        self.fetch_portfolio()
        self.fetch_watchlist()

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

            current_holdings.append({
                "ticker": ticker,
                "shares": round(shares, 4),
                "avg_buy": avg_buy,
                "price": price,
                "value": value,
                "pnl_pct": pnl_pct,
                "pe_ntm": dm.get_pe_ntm(ticker) or 0,
                "fcf_share": dm.get_fcf_per_share(ticker) or 0,
            })

        self.holdings = current_holdings
        self.total_value = round(current_total, 2)
        self.total_pnl = (
            round(((current_total - total_cost_all) / total_cost_all) * 100, 2)
            if total_cost_all > 0
            else 0.0
        )
        self.twr_metric = calculate_twr(trans_df, self.total_value)

    def fetch_watchlist(self):
        pass
