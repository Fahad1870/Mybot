import os
import time
import requests
from flask import Flask
import pandas as pd
import yfinance as yf

app = Flask(__name__)

TELEGRAM_TOKEN = "8347396776:AAHg4Az3FFAcJctx0H48zFfVA5vwP6g41PA"
TELEGRAM_CHAT_ID = "713758884"

def send_telegram_message(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            print(f"[TELEGRAM RESPONSE] {response.status_code} - {response.text}", flush=True)
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}", flush=True)

@app.route("/")
def home():
    return "Iron General Bot with Telegram is running 24/7!"

def run_bot():
    print("[INIT] Iron General BTC-USD Trading Bot Started...", flush=True)
    send_telegram_message("🚀 [Iron General] Bot started running on Render 24/7!")
    
    last_signal = None

    while True:
        try:
            data = yf.download("BTC-USD", period="5d", interval="1h", progress=False)
            if not data.empty:
                close_prices = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
                ema9 = close_prices.ewm(span=9, adjust=False).mean().iloc[-1]
                ema21 = close_prices.ewm(span=21, adjust=False).mean().iloc[-1]
                current_price = close_prices.iloc[-1]

                print(f"[LIVE MARKET DATA] BTC-USD Price: ${current_price:.2f} | EMA9: ${ema9:.2f} | EMA21: ${ema21:.2f}", flush=True)

                current_signal = "BUY" if ema9 > ema21 else "SELL"

                if current_signal != last_signal:
                    if current_signal == "BUY":
                        msg = f"🟢 [SIGNAL] BULLISH CROSSOVER!\nBTC Price: ${current_price:.2f}\nEMA9 (${ema9:.2f}) > EMA21 (${ema21:.2f})\nAction: Consider BUYING"
                    else:
                        msg = f"🔴 [SIGNAL] BEARISH CROSSOVER!\nBTC Price: ${current_price:.2f}\nEMA9 (${ema9:.2f}) < EMA21 (${ema21:.2f})\nAction: Consider SELLING"
                    
                    send_telegram_message(msg)
                    last_signal = current_signal

            time.sleep(60)
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
