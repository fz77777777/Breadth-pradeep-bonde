import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Stockbee NSE Breadth", layout="wide")

st.title("📈 Stockbee 20% Market Breadth Dashboard (NSE)")
st.markdown("This dashboard scans Indian stocks to find historical momentum shifts like Pradeep Bonde's model.")

# --- SIDEBAR CONFIGURATIONS ---
st.sidebar.header("⚙️ Scanner Settings")
lookback_days = st.sidebar.slider("Number of Days to Plot Chart", 10, 30, 15, help="Kitne din ka purana data chart par dekhna hai")

# --- CORE DATA ENGINE ---
def scan_individual_stocks(ticker_list, days_count):
    end_date = datetime.now()
    # Adding buffer days for 5-day momentum window calculation
    start_date = end_date - timedelta(days=days_count + 15)
    
    # Master dictionary to store final counts per date
    breadth_tracker = {}
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    total_tickers = len(ticker_list)
    
    for idx, ticker in enumerate(ticker_list):
        status_text.text(f"Scanning ({idx+1}/{total_tickers}): {ticker}")
        progress_bar.progress(int((idx + 1) / total_tickers * 100))
        
        try:
            # Single ticker data download fetch
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not df.empty and len(df) >= 6:
                # Core processing array loop
                for i in range(5, len(df)):
                    current_date = df.index[i].strftime('%Y-%m-%d')
                    
                    # Extracting scalar values safely from the matrix rows
                    close_today = float(df['Close'].iloc[i])
                    close_5d_ago = float(df['Close'].iloc[i-5])
                    
                    if close_5d_ago > 0:
                        pct_change = ((close_today - close_5d_ago) / close_5d_ago) * 100
                        
                        if current_date not in breadth_tracker:
                            breadth_tracker[current_date] = {'Up': 0, 'Down': 0}
                            
                        if pct_change >= 20.0:
                            breadth_tracker[current_date]['Up'] += 1
                        elif pct_change <= -20.0:
                            breadth_tracker[current_date]['Down'] += 1
        except Exception as e:
            continue
            
    status_text.empty()
    progress_bar.empty()
    
    # Formatting output to a clean structured DataFrame
    if breadth_tracker:
        formatted_df = pd.DataFrame.from_dict(breadth_tracker, orient='index').reset_index()
        formatted_df.columns = ['Date', 'Up_20pct', 'Down_20pct']
        formatted_df = formatted_df.sort_values(by='Date').tail(days_count)
        return formatted_df
    return pd.DataFrame()

# --- HARDCODED LIQUID NSE TICKERS POOL (Bypasses any network file fetch errors) ---
nse_universe = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
    "TATAMOTORS.NS", "AXISBANK.NS", "LT.NS", "KOTAKBANK.NS", "M&M.NS", "SUNPHARMA.NS", "NTPC.NS", "WIPRO.NS",
    "BAJAJFINSV.NS", "HCLTECH.NS", "ONGC.NS", "ADANIENT.NS", "COALINDIA.NS", "
