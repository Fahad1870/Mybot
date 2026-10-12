import os
import time
import sqlite3
import requests
from flask import Flask
import pandas as pd
import yfinance as yf

app = Flask(__name__)

# إعدادات تلجرام
TELEGRAM_TOKEN = "8347396776:AAHg4Az3FFAcJctX0H48zFfVA5vwP6g41PA"
TELEGRAM_CHAT_ID = "713758884"

# قائمة العملات والأصول المراد مراقبته
ASSETS = ["BTC-USD", "ETH-USD", "SOL-USD"]

# إعداد قاعدة البيانات المحلية SQLite لتسجيل الصفقات
def init_db():
    conn = sqlite3.connect("trading_bot.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            signal_type TEXT,
            price REAL,
            rsi REAL,
            stop_loss REAL,
            take_profit REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def log_trade_to_db(symbol, signal_type, price, rsi, sl, tp):
    try:
        conn = sqlite3.connect("trading_bot.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO signals (timestamp, symbol, signal_type, price, rsi, stop_loss, take_profit)
            VALUES (datetime('now'), ?, ?, ?, ?, ?, ?)
        """, (symbol, signal_type, price, rsi, sl, tp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] {e}", flush=True)

def send_telegram_message(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            print(f"[TELEGRAM RESPONSE] {response.status_code}", flush=True)
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}", flush=True)

@app.route("/")
def home():
    return "Pro Trading Bot with RSI, Multi-Asset & Risk Management is running 24/7!"

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def run_bot():
    print("[INIT] Pro Multi-Asset Trading Bot Started...", flush=True)
    send_telegram_message("🚀 *[Pro System]* Multi-Asset Trading Bot with RSI & Risk Management started running 24/7!")
    
    last_signals = {asset: None for asset in ASSETS}

    while True:
        for symbol in ASSETS:
            try:
                data = yf.download(symbol, period="5d", interval="1h", progress=False)
                if not data.empty:
                    close_prices = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
                    
                    # حساب المتوسطات ومؤشر RSI
                    ema9 = close_prices.ewm(span=9, adjust=False).mean().iloc[-1]
                    ema21 = close_prices.ewm(span=21, adjust=False).mean().iloc[-1]
                    rsi_series = calculate_rsi(close_prices)
                    current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
                    current_price = close_prices.iloc[-1]

                    print(f"[{symbol}] Price: ${current_price:.2f} | EMA9: ${ema9:.2f} \vert{} EMA21:${ema21:.2f} | RSI: {current_rsi:.2f}", flush=True)

                    # تحديد الإشارة مع فلتر RSI (منع الشراء فوق 70 ومنع البيع تحت 30)
                    current_signal = None
                    if ema9 > ema21 and current_rsi < 70:
                        current_signal = "BUY"
                    elif ema9 < ema21 and current_rsi > 30:
                        current_signal = "SELL"

                    # تنفيذ الإشعار إذا تغيرت الحالة
                    if current_signal and current_signal != last_signals[symbol]:
                        if current_signal == "BUY":
                            stop_loss = current_price * 0.98  # وقف خسارة 2%
                            take_profit = current_price * 1.04 # جني أرباح 4%
                            msg = (
                                f"🟢 *[PRO BULLISH SIGNAL]*\n"
                                f"🔹 Asset: `{symbol}`\n"
                                f"💰 Price: `${current_price:.2f}`\n"
                                f"📊 RSI: `{current_rsi:.2f}`\n"
                                f"📈 EMA9 > EMA21\n"
                                f"🛑 Stop Loss: `${stop_loss:.2f}`\n"
                                f"🎯 Take Profit: `${take_profit:.2f}`\n"
                                f"action: *BUY*"
                            )
                        else:
                            stop_loss = current_price * 1.02  # وقف خسارة 2%
                            take_profit = current_price * 0.96 # جني أرباح 4%
                            msg = (
                                f"🔴 *[PRO BEARISH SIGNAL]*\n"
                                f"🔹 Asset: `{symbol}`\n"
                                f"💰 Price: `${current_price:.2f}`\n"
                                f"📊 RSI: `{current_rsi:.2f}`\n"
                                f"📉 EMA9 < EMA21\n"
                                f"🛑 Stop Loss: `${stop_loss:.2f}`\n"
                                f"🎯 Take Profit: `${take_profit:.2f}`\n"
                                f"action: *SELL*"
                            )
                        
                        send_telegram_message(msg)
                        log_trade_to_db(symbol, current_signal, current_price, current_rsi, stop_loss, take_profit)
                        last_signals[symbol] = current_signal

                time.sleep(10) # الفاصل الزمني بين كل عملة وأخرى
            except Exception as e:
                print(f"[ERROR {symbol}] {e}", flush=True)
                time.sleep(15)

        time.sleep(30) # انتظار قبل دورة الفحص الجديدة

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
