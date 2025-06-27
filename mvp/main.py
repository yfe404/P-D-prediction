import ccxt
import time
from datetime import datetime
import csv
import os
import requests
import matplotlib.pyplot as plt
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuration
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
CSV_FILE = 'signals.csv'
HISTORY_LENGTH = 100
STACKING_THRESHOLD = 5
VOLUME_THRESHOLD_MULTIPLIER = 5
TRADE_THRESHOLD = 10
MIN_VOLUME_USDT = 100000  # Minimum volume to filter symbols


# API credentials for KuCoin (replace these with your actual API keys)
API_KEY = 
API_SECRET = 
API_PASSPHRASE = 

# Exchange setup with API keys
exchange = ccxt.kucoin({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSPHRASE,
    'enableRateLimit': True
})


# State
price_history = {}
volume_history = {}

# Ensure signal CSV file exists
if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Symbol", "Suspicion Score", "Reasons"])

# Helper: Telegram alerts
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# Function to fetch symbols with high volume
def get_high_volume_symbols(exchange, min_volume_usdt=100000):
    markets = exchange.load_markets()
    symbols = []

    for symbol, market in markets.items():
        if '/USDT' in symbol and market['active']:
            try:
                ticker = exchange.fetch_ticker(symbol)
                volume_usdt = ticker['quoteVolume']  # Already in USDT
                if volume_usdt and volume_usdt > min_volume_usdt:
                    symbols.append(symbol)
            except Exception as e:
                print(f"Failed to fetch {symbol}: {e}")
                continue

            time.sleep(0.2)  # to be safe even with rate limiter

    return symbols

# Helper: Plotting function for dashboard
def plot_data(symbol):
    plt.ion()
    fig, ax1 = plt.subplots()
    fig.suptitle(f'{symbol} - Price and Volume')

    while True:
        if symbol in price_history and symbol in volume_history:
            ax1.clear()
            ax2 = ax1.twinx()

            ax1.set_xlabel("Time (ticks)")
            ax1.set_ylabel("Price", color='blue')
            ax2.set_ylabel("Volume", color='orange')

            ax1.plot(price_history[symbol], color='blue')
            ax2.plot(volume_history[symbol], color='orange')

            plt.pause(1)

# Main detection function
def fetch_and_check(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        trades = exchange.fetch_trades(symbol)
        orderbook = exchange.fetch_order_book(symbol)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        last_price = ticker['last']
        quote_volume = ticker['quoteVolume']
        suspicion_score = 0
        reasons = []

        # Track price/volume history for charting
        if symbol not in price_history:
            price_history[symbol] = deque(maxlen=HISTORY_LENGTH)
            volume_history[symbol] = deque(maxlen=HISTORY_LENGTH)
        price_history[symbol].append(last_price)
        volume_history[symbol].append(quote_volume)

        # Volume spike
        avg_volume = sum(volume_history[symbol]) / len(volume_history[symbol])
        if quote_volume > avg_volume * VOLUME_THRESHOLD_MULTIPLIER:
            suspicion_score += 2
            reasons.append(f"Volume spike (Current: {quote_volume:.2f}, Avg: {avg_volume:.2f})")

        # Trade burst
        if len(trades) > TRADE_THRESHOLD:
            suspicion_score += 1
            reasons.append(f"Trade burst: {len(trades)} trades")

        # Price drift
        if len(price_history[symbol]) > 1:
            delta = last_price - price_history[symbol][0]
            if delta > 0:
                suspicion_score += 1
                reasons.append(f"Price increase: +{delta:.4f}")

        # Buy wall stacking
        top_price = last_price
        stacked = sum(1 for price, amount in orderbook['bids'][:10] if price < top_price and price * amount > 50)
        if stacked >= STACKING_THRESHOLD:
            suspicion_score += 2
            reasons.append(f"Buy wall stacking detected ({stacked} bids)")

        if suspicion_score >= 5:
            alert = f"[{now}] 🚨 ALERT on {symbol}: Score={suspicion_score} | Reasons: {', '.join(reasons)}"
            print(alert)
            send_telegram_message(alert)
            with open(CSV_FILE, mode='a', newline='') as file:
                csv.writer(file).writerow([now, symbol, suspicion_score, "; ".join(reasons)])

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

# Parallel scanner
def scan_all_coins(symbols):
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_and_check, symbols)

# Main loop
if __name__ == '__main__':
    # Get high volume symbols
    candidates = get_high_volume_symbols(exchange, MIN_VOLUME_USDT)
    last_refresh_time = time.time()

    # Optional: launch a visual dashboard thread for a key coin
#    threading.Thread(target=plot_data, args=("PUNDIX/USDT",), daemon=True).start()

    while True:
        print(f"\nChecking coins at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}...")
        scan_all_coins(candidates)

        if time.time() - last_refresh_time > 3600:
            print("\nRefreshing candidate coins...")
            candidates = get_high_volume_symbols(exchange, MIN_VOLUME_USDT)
            last_refresh_time = time.time()

        time.sleep(15)
