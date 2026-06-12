import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Configurations for Mobile & Cloud Layout
st.set_page_config(page_title="Stockbee Breadth NSE", layout="wide", page_icon="📈")

st.title("📈 Stockbee 20% Market Breadth Dashboard (NSE)")
st.markdown("Track **Extreme Panic & Institutional Accumulation** across Indian Stocks.")

# -----------------------------------------------------------------
# CLOUD OPTIMIZED STOCK LIST ENGINE
# -----------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_nse_stock_universe():
    """Fetches clean pre-filtered active liquid stock tokens for index analysis"""
    try:
        # Fetching a production-ready clean Nifty Total Market list from secondary stable mirror
        url = "https://raw.githubusercontent.com/anirbanghoshsbi/NSE-LIST-OF-STOCKS/main/ind_niftytotalmarket_list.csv"
        df = pd.read_csv(url)
        symbols = df['Symbol'].dropna().unique().tolist()
        yf_symbols = [f"{str(sym).strip()}.NS" for sym in symbols if len(str(sym).strip()) > 0]
        return yf_symbols
    except Exception as e:
        # High reliability fallback list if server mirror times out during boot
        return [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
            "BHARTIARTL.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "TATAMOTORS.NS"
        ]

@st.cache_data(ttl=1800)  # Heavy caching to prevent Streamlit Cloud runtime timeouts
def calculate_breadth_metrics(tickers, lookback_days=45):
    """Processes historical structures via vectorized blocks safely on shared cloud infrastructure"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days + 15)
    
    # Download as a single matrix bundle
    data = yf.download(tickers, start=start_date, end=end_date, interval="1d", group_by='ticker', progress=False)
    
    if data.empty:
        return pd.DataFrame()
        
    # Standardizing dates across the active indexes
    trading_days = data.index[-lookback_days:]
    
    historical_dates = []
    up_counts = []
    down_counts = []
    total_active_counts = []
    
    # Extraction Engine
    for idx in trading_days:
        ups = 0
        downs = 0
        actives = 0
        
        for ticker in tickers:
            try:
                if ticker in data.columns.levels[0]:
                    ticker_df = data[ticker]
                    if idx in ticker_df.index:
                        pos = ticker_df.index.get_loc(idx)
                        if pos >= 5:  # 5-Day momentum calculation window
                            curr_close = ticker_df['Close'].iloc[pos]
                            prev_5d_close = ticker_df['Close'].iloc[pos - 5]
                            
                            if pd.notna(curr_close) and pd.notna(prev_5d_close) and prev_5d_close > 0:
                                pct_change = ((curr_close - prev_5d_close) / prev_5d_close) * 100
                                actives += 1
                                if pct_change >= 20.0:
                                    ups += 1
                                elif pct_change <= -20.0:
                                    downs += 1
            except:
                continue
                
        if actives > 0:
            historical_dates.append(idx)
            up_counts.append(ups)
            down_counts.append(downs)
            total_active_counts.append(actives)
            
    return pd.DataFrame({
        'Date': historical_dates,
        'Stocks_Up_20pct': up_counts,
        'Stocks_Down_20pct': down_counts,
        'Total_Active': total_active_counts
    })

# Execution Circuit
all_tickers = load_nse_stock_universe()
# Optimizing the slice size to 500-1000 high momentum stocks to stay within Streamlit Cloud's free RAM limits
active_pool = all_tickers[:750] 

st.sidebar.header("⚙️ Scanner Configurations")
lookback_window = st.sidebar.slider("Historical Window (Days)", 20, 60, 40)
panic_threshold = st.sidebar.slider("Panic Reversal Trigger (Count)", 5, 50, 15)

with st.spinner("Analyzing Market Vectors... This takes a moment on Cloud Boot"):
    breadth_data = calculate_breadth_metrics(active_pool, lookback_days=lookback_window)

# Rendering Engine
if not breadth_data.empty:
    latest_row = breadth_data.iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("5-Day DOWN 20% Count", int(latest_row['Stocks_Down_20pct']))
    with c2:
        st.metric("5-Day UP 20% Count", int(latest_row['Stocks_Up_20pct']))
    with c3:
        status = "🚨 BOUNCE IMMINENT" if latest_row['Stocks_Down_20pct'] >= panic_threshold else "✅ Normal"
        st.metric("Market Status", status)
        
    if latest_row['Stocks_Down_20pct'] >= panic_threshold:
        st.error(f"🔥 Pradeep Bonde Model Triggered! Extreme institutional capitulation detected. Look for sharp immediate long reversals.")

    # Chart Processing
    fig = go.Figure()
    fig.add_trace(go.Bar(x=breadth_data['Date'], y=breadth_data['Stocks_Down_20pct'], name='Down 20% (Panic)', marker_color='#EF5350'))
    fig.add_trace(go.Bar(x=breadth_data['Date'], y=breadth_data['Stocks_Up_20pct'], name='Up 20% (Expansion)', marker_color='#26A69A'))
    
    fig.add_shape(type="line", x0=breadth_data['Date'].iloc[0], y0=panic_threshold, x1=breadth_data['Date'].iloc[-1], y1=panic_threshold,
                  line=dict(color="White", width=1, dash="dash"))
                  
    fig.update_layout(template="plotly_dark", hovermode="x unified", height=500, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Loading telemetry arrays... Refresh the browser if dashboard does not render in 30 seconds.")
