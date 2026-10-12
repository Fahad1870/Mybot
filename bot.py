import os
import time
from dotenv import load_dotenv

# Load risk limits from .env configuration
load_dotenv()
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", 0.03))
MAX_POSITION_SIZE_PCT = float(os.getenv("MAX_POSITION_SIZE_PCT", 0.10))

print("=== Iron General Trading Bot Initialized ===")
print(f"Risk Limits Loaded -> Max Daily Loss: {MAX_DAILY_LOSS_PCT * 100}% | Max Position: {MAX_POSITION_SIZE_PCT * 100}%")
print("Status: Running Paper Trading Loop...")

# Simulated trading loop
try:
    while True:
        # Placeholder for EMA Crossover and Order Flow Imbalance logic
        print("[INFO] Checking market signals (EMA Crossover & Order Flow)... No trade triggered yet.")
        time.sleep(5)
except KeyboardInterrupt:
    print("\n[INFO] Bot stopped safely by user.")
