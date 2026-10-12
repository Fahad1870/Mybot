import os
import time
from flask import Flask
import pandas as pd
import yfinance as yf

app = Flask(__name__)


@app.route("/")
def home():
  return "Iron General Bot is running 24/7!"


def run_bot():
  print("[INIT] Iron General BTC-USD Trading Bot Started...")
  while True:
    try:
      data = yf.download(
          "BTC-USD", period="5d", interval="1h", progress=False
      )
      if not data.empty:
        close_prices = (
            data["Close"].iloc[:, 0]
            if isinstance(data["Close"], pd.DataFrame)
            else data["Close"]
        )
        ema9 = close_prices.ewm(span=9, adjust=False).mean().iloc[-1]
        ema21 = close_prices.ewm(span=21, adjust=False).mean().iloc[-1]
        current_price = close_prices.iloc[-1]

        print(
            f"[LIVE MARKET DATA] BTC-USD Price: ${current_price:.2f} | EMA9:"
            f" ${ema9:.2f} | EMA21: ${ema21:.2f}"
        )

        if ema9 > ema21:
          print("-> [SIGNAL] BULLISH (EMA 9 > EMA 21) - Potential BUY")
        else:
          print("-> [SIGNAL] BEARISH (EMA 9 < EMA 21) - Potential SELL")

      time.sleep(60)
    except Exception as e:
      print(f"[ERROR] {e}")
      time.sleep(30)


if __name__ == "__main__":
  import threading

  t = threading.Thread(target=run_bot)
  t.daemon = True
  t.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)

