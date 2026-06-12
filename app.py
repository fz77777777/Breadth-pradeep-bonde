import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stockbee NSE Breadth", layout="wide")

st.title("📈 Stockbee 20% Market Breadth Dashboard (NSE)")
st.markdown("This dashboard scans Indian stocks to find historical momentum shifts like Pradeep Bonde's model.")

# --- SIDEBAR CONFIGURATIONS ---
st.sidebar.header("⚙️ Scanner Settings")
lookback_days = st.sidebar.slider("Number of Days to Plot Chart", 10, 30, 20)

# --- CORE DATA ENGINE ---
def scan_individual_stocks(ticker_list, days_count):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_count + 20)
    
    breadth_tracker = {}
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    total_tickers = len(ticker_list)
    
    for idx, ticker in enumerate(ticker_list):
        status_text.text(f"Scanning ({idx+1}/{total_tickers}): {ticker}")
        progress_bar.progress(int((idx + 1) / total_tickers * 100))
        
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if not df.empty and len(df) >= 6:
                # Standardizing multiindex structures safely
                if isinstance(df.columns, pd.MultiIndex):
                    close_series = df.xs('Close', axis=1, level=0).iloc[:, 0]
                else:
                    close_series = df['Close']
                
                close_series = close_series.dropna()
                
                for i in range(5, len(close_series)):
                    current_date = close_series.index[i].strftime('%Y-%m-%d')
                    
                    close_today = float(close_series.iloc[i])
                    close_5d_ago = float(close_series.iloc[i-5])
                    
                    if close_5d_ago > 0:
                        pct_change = ((close_today - close_5d_ago) / close_5d_ago) * 100
                        
                        if current_date not in breadth_tracker:
                            breadth_tracker[current_date] = {'Up': 0, 'Down': 0}
                            
                        if pct_change >= 20.0:
                            breadth_tracker[current_date]['Up'] += 1
                        elif pct_change <= -20.0:
                            breadth_tracker[current_date]['Down'] += 1
        except:
            continue
            
    status_text.empty()
    progress_bar.empty()
    
    if breadth_tracker:
        formatted_df = pd.DataFrame.from_dict(breadth_tracker, orient='index').reset_index()
        formatted_df.columns = ['Date', 'Up_20pct', 'Down_20pct']
        formatted_df = formatted_df.sort_values(by='Date').tail(days_count)
        return formatted_df
    return pd.DataFrame()

# --- FIXED SHORT CLEAN UNIVERSE POOL ---
nse_universe = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "TATAMOTORS.NS", "AXISBANK.NS", 
    "LT.NS", "KOTAKBANK.NS", "M&M.NS", "SUNPHARMA.NS", "WIPRO.NS"
]

st.warning("👉 Click the button below to execute the live market breadth computation model.")

# --- ACTION TRIGGER ---
if st.button("🚀 Run Market Breadth Scan", type="primary"):
    with st.spinner("Processing calculations..."):
        result_df = scan_individual_stocks(nse_universe, lookback_days)
        
    if not result_df.empty:
        st.success("Scan Completed!")
        
        latest = result_df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("Latest 5-Day Up 20% Count", int(latest['Up_20pct']))
        c2.metric("Latest 5-Day Down 20% Count", int(latest['Down_20pct']))
        
        # --- GRAPH INTERFACE ---
        st.subheader("📊 Stockbee 20% Breadth Visuals")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=result_df['Date'], y=result_df['Down_20pct'], name='5-Day Down 20% (Panic)', marker_color='#EF5350'))
        fig.add_trace(go.Bar(x=result_df['Date'], y=result_df['Up_20pct'], name='5-Day Up 20% (Thrust)', marker_color='#26A69A'))
        
        fig.update_layout(
            template="plotly_dark",
            barmode='group',
            hovermode="x unified",
            height=480,
            margin=dict(l=20, r=20, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Engine failed to resolve values. Click run again.")
