import sys
import os
# Añadir path raíz para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_engine import DataManager
from utils.ai_engine import analyze_news_impact
from supabase import create_client
import requests

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
dm = DataManager()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        print(f"Telegram Response ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_sync():
    print("Starting Daily Sync...")
    
    # 1. Obtener Tickers únicos de la DB
    assets = supabase.table("assets").select("ticker").execute().data
    
    report_lines = []
    
    for asset in assets:
        ticker = asset['ticker']
        print(f"Processing {ticker}...")
        
        # Update Price & Fundamentals
        price = dm.get_current_price(ticker)
        pe = dm.get_pe_ntm(ticker)
        fcf = dm.get_fcf_per_share(ticker)
        
        # Update DB
        supabase.table("assets").update({
            "last_price": price,
            "pe_ntm": pe,
            "fcf_share": fcf,
            "last_updated": "now()"
        }).eq("ticker", ticker).execute()
        
        # AI News Check (Mockup de fetch de noticias)
        # En prod: dm.get_news(ticker)
        news_sample = [f"{ticker} reports strong earnings growth.", "Market outlook positive."]
        ai_analysis = analyze_news_impact(news_sample)
        
        if ai_analysis['impact_level'] == 'high':
            report_lines.append(f"🚨 {ticker}: {ai_analysis['summary']} (Sent: {ai_analysis['sentiment']})")

    # Send Notification
    if report_lines:
        msg = "🚀 *SmartFolio Daily Alert:*\n\n" + "\n".join(report_lines)
    else:
        msg = f"✅ *SmartFolio Sync Complete*\nUpdated {len(assets)} assets.\nNo high impact news detected."
    
    send_telegram(msg)
    
    print("Sync Complete.")

if __name__ == "__main__":
    run_sync()
