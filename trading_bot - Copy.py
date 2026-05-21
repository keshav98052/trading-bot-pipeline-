import joblib
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER dictionary (it will automatically skip if you already have it)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Initialize the VADER brain
vader = SentimentIntensityAnalyzer()
print("📚 VADER NLP module loaded and ready to read.")
import os
import sqlite3
import time
import schedule
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ==========================================
# 1. AUTHENTICATION 
# ==========================================
ALPACA_KEY = "PK2ROLAUKPTFHUVSJVDJJJRV3U" 
ALPACA_SECRET = "6CgJoYBhCZJouHnhuhHUSDHhdHdshHdhh1Fv4L6gH79"

trading_client = TradingClient(api_key=ALPACA_KEY, secret_key=ALPACA_SECRET, paper=True)
news_client = NewsClient(api_key=ALPACA_KEY, secret_key=ALPACA_SECRET, raw_data=True)
data_client = StockHistoricalDataClient(api_key=ALPACA_KEY, secret_key=ALPACA_SECRET)

# ==========================================
# 2. HELPER FUNCTIONS (The Tools)
# ==========================================
def get_live_asset_data(ticker):
    # Fetch News
    news_req = NewsRequest(symbols=ticker, limit=1) 
    news_response = news_client.get_news(news_req)
    articles = news_response.get("news", [])
    latest_headline = articles[0].get("headline") if articles else "No recent news."
    
    # Fetch Momentum
    start_time = datetime.now() - timedelta(days=5) 
    bars_req = StockBarsRequest(symbol_or_symbols=[ticker], timeframe=TimeFrame.Day, start=start_time)
    bars_response = data_client.get_stock_bars(bars_req)
    
    if ticker in bars_response.data and len(bars_response.data[ticker]) >= 2:
        recent_bars = bars_response.data[ticker]
        recent_return = (recent_bars[-1].close - recent_bars[-2].close) / recent_bars[-2].close
    else:
        recent_return = 0.0

    return {"Ticker": ticker, "Latest_Headline": latest_headline, "Recent_Return": recent_return}

# ---> NEW: Load the AI Brain into memory <---
try:
    import joblib
    import pandas as pd
    trained_ai = joblib.load("stock_prediction.pkl")
    print("🧠 AI Brain successfully loaded into the bot.")
except Exception as e:
    print(f"⚠️ WARNING: Could not load stock_prediction.pkl: {e}")
    trained_ai = None

def get_model_prediction(ticker, headline, daily_return):
    """
    Uses VADER NLP to read the news, then asks the Random Forest model to predict the next move.
    """
    if trained_ai is None:
        return -1 # Default to HOLD if the ML brain is missing
        
    # ---> NEW: Real NLP Sentiment Analysis <---
    if headline == "No recent news.":
        sentiment_score = 0.0 # Neutral if there is no news to read
    else:
        # VADER reads the text and generates a 'compound' score from -1.0 to 1.0
        sentiment_dict = vader.polarity_scores(headline)
        sentiment_score = sentiment_dict['compound']
        
    # Print what the AI thought of the news to the terminal
    print(f"   📰 NLP Score for {ticker}: {sentiment_score:.2f} | Headline: '{headline[:40]}...'")
    
    # Format the live data exactly how the AI was trained to see it
    live_features = pd.DataFrame({
        "recent_return": [daily_return], 
        "sentiment_score": [sentiment_score]
    })
    
    # Ask the ML model to predict (Returns 1 for Buy, 0 for Sell)
    prediction = trained_ai.predict(live_features)[0]
    
    return int(prediction)

def log_to_database(ticker, headline, recent_return, prediction_signal):
    conn = sqlite3.connect('market_memory.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_features 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, 
                      ticker TEXT, headline TEXT, recent_return REAL, prediction_signal INTEGER)''')
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO daily_features (timestamp, ticker, headline, recent_return, prediction_signal) VALUES (?, ?, ?, ?, ?)', 
                   (current_time, ticker, headline, recent_return, prediction_signal))
    conn.commit()
    conn.close()

# ==========================================
# # ==========================================
# 3. THE WRAPPER (The Box)
# ==========================================
# Everything indented inside this function will ONLY run when the alarm clock goes off.
def run_trading_bot():
    print(f"\n=========================================")
    print(f"🤖 WAKING UP BOT AT {datetime.now()}")
    print(f"=========================================")
    
    # ---> UPDATE 1: Add as many companies as you want here <---
    target_watchlist = [
        "AAPL", "TSLA", "MSFT", "NVDA", 
        "AMZN", "GOOGL", "META", "NFLX"
    ]
    
    live_market_snapshot = []
    
    for ticker in target_watchlist:
        try:
            live_market_snapshot.append(get_live_asset_data(ticker))
            
            # ---> UPDATE 2: The 1-second pause to protect your API access <---
            time.sleep(1) 
            
        except Exception as e:
            print(f"❌ Data fetch failed for {ticker}: {e}")

    try:
        open_positions = {p.symbol: int(p.qty) for p in trading_client.get_all_positions()}
    except:
        open_positions = {}

    for asset in live_market_snapshot:
        symbol = asset["Ticker"]
        prediction = get_model_prediction(symbol, asset["Latest_Headline"], asset["Recent_Return"])
        
        log_to_database(symbol, asset["Latest_Headline"], asset["Recent_Return"], prediction)
        
        if prediction == 1 and symbol not in open_positions:
            buy_order = MarketOrderRequest(symbol=symbol, qty=5, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
            trading_client.submit_order(order_data=buy_order)
            print(f"✅ BUY Executed: 5 shares of {symbol}")
            
        elif prediction == 0 and symbol in open_positions:
            sell_order = MarketOrderRequest(symbol=symbol, qty=open_positions[symbol], side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
            trading_client.submit_order(order_data=sell_order)
            print(f"✅ SELL Executed: Liquidated {symbol}")

    print("🏁 Daily Trading Run Complete. Going back to sleep.")

# ==========================================
# 4. THE ALARM CLOCK
# ==========================================
# This schedules the "box" we created above to open at a specific time.
schedule.every().day.at("09:45").do(run_trading_bot)

print("🟢 Trading Bot is live. Waiting for the scheduled time...")

# This infinite loop keeps the Python script awake so it can check the clock.
while True:
    schedule.run_pending()
    time.sleep(60) # Sleep for 60 seconds to save computer power, then check the clock again