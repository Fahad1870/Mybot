import os
import time
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv

# Load risk limits from .env configuration
load_dotenv()
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", 0.03))
MAX_POSITION_SIZE_PCT = float(os.getenv("MAX_POSITION_SIZE_PCT", 0.10))

SYMBOL = "BTC-USD"  # رمز البيتكوين مقابل الدولار

print(f"=== Iron General Trading Bot Initialized ===")
print(f"Target Asset: {SYMBOL}")
print(f"Risk Limits -> Max Daily Loss: {MAX_DAILY_LOSS_PCT * 100}% | Max Position: {MAX_POSITION_SIZE_PCT * 100}%")
print("Status: Fetching Live Market Data...\n")

def check_market_signals():
    # Fetch latest minute data from Yahoo Finance
    data = yf.download(tickers=SYMBOL, period="1d", interval="1m", progress=False)
    
    if data.empty:
        print("[WARNING] Could not fetch market data. Retrying...")
        return

    # Calculate EMA 9 and EMA 21
    data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()

    latest_price = data['Close'].iloc[-1].item()
    ema9 = data['EMA9'].iloc[-1].item()
    ema21 = data['EMA21'].iloc[-1].item()

    print(f"[LIVE MARKET DATA] {SYMBOL} Price: ${latest_price:.2f} | EMA9: ${ema9:.2f} | EMA21: ${ema21:.2f}")

    # Signal Logic
    if ema9 > ema21:
        print(" -> [SIGNAL] BULLISH (EMA 9 > EMA 21) - Potential BUY")
    elif ema9 < ema21:
        print(" -> [SIGNAL] BEARISH (EMA 9 < EMA 21) - Potential SELL")
    else:
        print(" -> [SIGNAL] NEUTRAL")

try:
    while True:
        check_market_signals()
        time.sleep(10)  # Check every 10 seconds
except KeyboardInterrupt:
    print("\n[INFO] Bot stopped safely by user.")
