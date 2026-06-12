import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stockbee NSE", layout="wide")

st.title("📈 Stockbee 20% Market Breadth (NSE)")

@st.cache_data(ttl=3600)
def get_stock_data():
    # Production-ready liquid core assets list to avoid memory collapse
    tickers = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
        "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "TATAMOTORS.NS", "AXISBANK.NS",
        "WIPRO.NS", "HCLTECH.NS", "SUNPHARMA.NS", "NTPC.NS", "M&M.NS"
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=40)
    
    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker', progress=False)
    
    trading_days = data.index[-20:]
    dates, ups, downs = [], [], []
    
    for idx in trading_days:
        u, d = 0, 0
        for t in tickers:
            try:
                t_df = data[t]
                if idx in t_df.index:
                    pos = t_df.index.get_loc(idx)
                    if pos >= 5:
                        c = t_df['Close'].iloc[pos]
                        p = t_df['Close'].iloc[pos-5]
                        pct = ((c - p) / p) * 100
                        if pct >= 20: u += 1
                        elif pct <= -20: d += 1
            except: continue
        dates.append(idx)
        ups.append(u)
        downs.append(d)
        
    return pd.DataFrame({'Date': dates, 'Up': ups, 'Down': downs})

with st.spinner("Fetching Market Data..."):
    df = get_stock_data()

if not df.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Date'], y=df['Down'], name='5-Day Down 20%', marker_color='red'))
    fig.add_trace(go.Bar(x=df['Date'], y=df['Up'], name='5-Day Up 20%', marker_color='green'))
    fig.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig, use_container_width=True)
