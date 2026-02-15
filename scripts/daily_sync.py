"""
SmartFolio Daily Sync — Intelligent Alerts Engine
Ejecutado vía GitHub Actions (cron) o manualmente.

Scanners:
1. Earnings Calendar (próximos 7 días)
2. Price Drop Monitor (≥5% caída diaria)
3. PE Undervaluation (PE actual < 90% del guardado en DB)
4. AI News Analysis (filtrado por portfolio)
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_engine import DataManager
from utils.ai_engine import analyze_news_impact
from supabase import create_client
import requests
from typing import List

# ── Config ────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
dm = DataManager()


def send_telegram(message: str) -> None:
    """Envía mensaje a Telegram con parse_mode Markdown."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
        print(f"Telegram Response ({resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"Telegram Error: {e}")


def get_portfolio_tickers() -> List[str]:
    """Obtiene tickers únicos del portfolio (transacciones)."""
    data = supabase.table("transactions").select("ticker").execute().data
    return list({item["ticker"] for item in data}) if data else []


def scan_earnings(tickers: List[str]) -> List[str]:
    """Scanner 1: Earnings en los próximos 7 días."""
    lines = []
    earnings = dm.get_earnings_calendar(tickers, days=7)
    for e in earnings:
        eps_est = e.get("eps_estimated", "N/A")
        lines.append(f"• {e['ticker']} reporta el {e['date']} (EPS est: {eps_est})")
    return lines


def scan_price_drops(tickers: List[str]) -> List[str]:
    """Scanner 2: Caídas de precio ≥5% en el día."""
    lines = []
    for ticker in tickers:
        change = dm.get_daily_price_change(ticker)
        if change is not None and change <= -5.0:
            lines.append(f"• {ticker} cayó *{change}%* hoy")
        elif change is not None and change >= 5.0:
            lines.append(f"• {ticker} subió *+{change}%* hoy 🚀")
    return lines


def scan_pe_undervaluation(tickers: List[str]) -> List[str]:
    """Scanner 3: PE actual < 90% del PE guardado en DB (subvaluación)."""
    lines = []
    for ticker in tickers:
        # Obtener PE guardado en DB como referencia histórica
        asset = supabase.table("assets").select("pe_ntm").eq("ticker", ticker).execute()
        if not asset.data or not asset.data[0].get("pe_ntm"):
            continue
        historical_pe = float(asset.data[0]["pe_ntm"])

        current_pe = dm.get_pe_ntm(ticker)
        if current_pe is None or historical_pe <= 0:
            continue

        ratio = current_pe / historical_pe
        if ratio < 0.9:
            drop_pct = round((1 - ratio) * 100, 1)
            lines.append(
                f"• {ticker} PE {current_pe} vs histórico {historical_pe} (*-{drop_pct}%*)"
            )
    return lines


def update_prices_and_fundamentals(tickers: List[str]) -> int:
    """Actualiza precios y fundamentales en la DB."""
    updated = 0
    for ticker in tickers:
        print(f"  Updating {ticker}...")
        price = dm.get_current_price(ticker)
        pe = dm.get_pe_ntm(ticker)
        fcf = dm.get_fcf_per_share(ticker)

        update_data = {"last_price": price, "last_updated": "now()"}
        if pe is not None:
            update_data["pe_ntm"] = pe
        if fcf is not None:
            update_data["fcf_share"] = fcf

        supabase.table("assets").update(update_data).eq("ticker", ticker).execute()
        updated += 1
    return updated


def run_sync():
    """Ejecuta el sync diario completo."""
    print("=" * 50)
    print("SmartFolio Daily Sync — Starting...")
    print("=" * 50)

    # ── Obtener Tickers del Portfolio ──
    tickers = get_portfolio_tickers()
    if not tickers:
        print("No tickers in portfolio. Nothing to sync.")
        send_telegram("ℹ️ *SmartFolio*: No hay posiciones en el portfolio.")
        return

    print(f"Portfolio tickers: {tickers}")

    # ── Actualizar Precios ──
    print("\n📊 Updating prices & fundamentals...")
    updated_count = update_prices_and_fundamentals(tickers)

    # ── Scanner 1: Earnings ──
    print("\n📅 Scanning earnings calendar...")
    earnings_lines = scan_earnings(tickers)

    # ── Scanner 2: Price Drops ──
    print("\n📉 Scanning price movements...")
    price_lines = scan_price_drops(tickers)

    # ── Scanner 3: PE Undervaluation ──
    print("\n💎 Scanning PE undervaluation...")
    pe_lines = scan_pe_undervaluation(tickers)

    # ── Scanner 4: AI News (filtrado por portfolio) ──
    print("\n🤖 Running AI news analysis...")
    ai_lines = []
    for ticker in tickers:
        # Usar noticias reales de FMP si disponible, sino mock
        news_data = dm._get_fmp(f"stock_news", {"tickers": ticker, "limit": 3})
        if news_data:
            news_texts = [n.get("text", n.get("title", "")) for n in news_data[:3]]
        else:
            news_texts = [f"{ticker} market update."]

        analysis = analyze_news_impact(news_texts)
        if analysis.get("impact_level") in ("high", "med"):
            sentiment_emoji = "🟢" if analysis.get("sentiment", 0) > 0 else "🔴"
            ai_lines.append(
                f"• {sentiment_emoji} {ticker}: {analysis.get('summary', 'N/A')}"
            )

    # ── Construir Reporte ──
    report_sections = ["🚀 *SmartFolio Daily Report*", ""]

    if earnings_lines:
        report_sections.append("📊 *EARNINGS PRÓXIMOS (7d):*")
        report_sections.extend(earnings_lines)
        report_sections.append("")

    if price_lines:
        report_sections.append("⚠️ *MOVIMIENTOS FUERTES:*")
        report_sections.extend(price_lines)
        report_sections.append("")

    if pe_lines:
        report_sections.append("💎 *SUBVALUACIÓN DETECTADA:*")
        report_sections.extend(pe_lines)
        report_sections.append("")

    if ai_lines:
        report_sections.append("🤖 *ANÁLISIS IA:*")
        report_sections.extend(ai_lines)
        report_sections.append("")

    if not (earnings_lines or price_lines or pe_lines or ai_lines):
        report_sections.append(f"✅ Updated {updated_count} assets. No alerts today.")

    report = "\n".join(report_sections)
    print(f"\n{'=' * 50}")
    print(report)
    print(f"{'=' * 50}")

    send_telegram(report)
    print("\nSync Complete. ✅")


if __name__ == "__main__":
    run_sync()
