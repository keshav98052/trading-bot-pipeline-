import streamlit as st
import sqlite3
import pandas as pd
from alpaca.trading.client import TradingClient

# ==========================================
# 1. AUTHENTICATION (Use your NEW keys here!)
# ==========================================
ALPACA_KEY = "PK2ROLAUKDSIICSDSIDJMRV3U"
ALPACA_SECRET = "6CgJoYBhCZJouHhjhJhdhsh34h4h3ydhFv4L6gH79"

# The dashboard only needs the trading client to check your balances
trading_client = TradingClient(api_key=ALPACA_KEY, secret_key=ALPACA_SECRET, paper=True)

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("🤖 Live Trading Bot Monitor")

# ==========================================
# 2. LIVE ACCOUNT PERFORMANCE
# ==========================================
st.subheader("💰 Portfolio Overview")

try:
    # Fetch live account data from Alpaca
    account = trading_client.get_account()
    
    # Alpaca paper accounts start at $100,000 by default
    initial_balance = 100000.00
    current_value = float(account.portfolio_value)
    cash_available = float(account.cash)
    
    # Calculate Total Profit/Loss
    total_profit_loss = current_value - initial_balance
    profit_percentage = (total_profit_loss / initial_balance) * 100

    # Display beautifully using Streamlit metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Portfolio Value", 
            value=f"${current_value:,.2f}", 
            delta=f"${total_profit_loss:,.2f} ({profit_percentage:.2f}%)"
        )
    with col2:
        st.metric(label="Buying Power (Cash)", value=f"${cash_available:,.2f}")
    with col3:
        # Fetch how many companies you currently own shares of
        positions = trading_client.get_all_positions()
        st.metric(label="Active Stock Positions", value=len(positions))
        
except Exception as e:
    st.error(f"Could not connect to Alpaca to fetch balances: {e}")

st.divider()

# ==========================================
# 3. LATEST AI SIGNALS
# ==========================================
st.subheader("Latest Signals")

try:
    conn = sqlite3.connect('market_memory.db')
    df = pd.read_sql_query("SELECT * FROM daily_features ORDER BY timestamp DESC", conn)
    conn.close()
    
    # Keep only the single most recent row for each unique ticker symbol
    latest_run = df.drop_duplicates(subset=['ticker'], keep='first')
    
    # Dynamically size the columns based on the number of stocks in your watchlist
    num_stocks = len(latest_run)
    if num_stocks > 0:
        cols = st.columns(num_stocks if num_stocks < 8 else 8) # Max 8 across
        
        for index, row in latest_run.head(8).reset_index().iterrows():
            col = cols[index % len(cols)] 
            
            with col:
                if row['prediction_signal'] == 1:
                    signal_text = "🟢 INVEST / BUY"
                elif row['prediction_signal'] == 0:
                    signal_text = "🔴 DIVEST / SELL"
                else:
                    signal_text = "⚪ HOLD / NEUTRAL"
                    
                st.info(f"**{row['ticker']}**")
                st.write(f"**Action:** {signal_text}")
                st.metric(label="24hr Momentum", value=f"{row['recent_return'] * 100:.2f}%")
                st.caption(f"News: {row['headline']}")
    else:
        st.write("No predictions logged yet. Let the bot run once to populate this section.")

except Exception as e:
    st.error(f"Could not load database: {e}")

# ==========================================
# 4. HISTORICAL MEMORY LOG
# ==========================================
st.divider()
st.subheader("Historical Memory Log")

try:
    def highlight_signals(val):
        if val == 1:
            return 'background-color: #004d00' 
        elif val == 0:
            return 'background-color: #4d0000' 
        return ''

    styled_df = df.style.map(highlight_signals, subset=['prediction_signal'])
    st.dataframe(styled_df, use_container_width=True)
except:
    pass