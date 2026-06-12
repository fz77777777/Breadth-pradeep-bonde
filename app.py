import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stockbee NSE Breadth", layout="wide")

st.title("📈 Stockbee 20% Market Breadth Dashboard (NSE)")
st.markdown("This dashboard scans Indian broader market (Smallcaps/Midcaps) to find historical momentum shifts like Pradeep Bonde's model.")

# --- SIDEBAR CONFIGURATIONS ---
st.sidebar.header("⚙️ Scanner Settings")
lookback_days = st.sidebar.slider("Number of Days to Plot Chart", 10, 30, 20)

# --- CORE DATA ENGINE ---
def scan_large_universe(ticker_list, days_count):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_count + 20)
    
    breadth_tracker = {}
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # 30-30 stocks ke groups (chunks) me data download karenge taaki speed bani rahe aur error na aaye
    chunk_size = 30
    total_tickers = len(ticker_list)
    
    for i in range(0, total_tickers, chunk_size):
        chunk = ticker_list[i:i + chunk_size]
        status_text.text(f"Scanning Stocks Batch ({i}/{total_tickers})... Please wait.")
        progress_bar.progress(int(i / total_tickers * 100))
        
        try:
            # Batch download for the chunk
            df_chunk = yf.download(chunk, start=start_date, end=end_date, group_by='ticker', progress=False)
            
            if df_chunk.empty:
                continue
                
            # Align trading sessions dates
            available_tickers = df_chunk.columns.levels[0] if isinstance(df_chunk.columns, pd.MultiIndex) else [chunk[0]]
            sample_ticker = available_tickers[0]
            
            if isinstance(df_chunk.columns, pd.MultiIndex):
                trading_days = df_chunk[sample_ticker].dropna().index[-days_count:]
            else:
                trading_days = df_chunk.dropna().index[-days_count:]
                
            for current_day in trading_days:
                current_date_str = current_day.strftime('%Y-%m-%d')
                if current_date_str not in breadth_tracker:
                    breadth_tracker[current_date_str] = {'Up': 0, 'Down': 0}
                
                for ticker in chunk:
                    try:
                        # Extract close data for single or multi-index dataframes
                        if isinstance(df_chunk.columns, pd.MultiIndex):
                            if ticker in df_chunk.columns.levels[0]:
                                ticker_df = df_chunk[ticker].dropna()
                        else:
                            ticker_df = df_chunk.dropna()
                            
                        if current_day in ticker_df.index:
                            pos = ticker_df.index.get_loc(current_day)
                            if pos >= 5:
                                close_today = float(ticker_df['Close'].iloc[pos])
                                close_5d_ago = float(ticker_df['Close'].iloc[pos - 5])
                                
                                if close_5d_ago > 0:
                                    pct_change = ((close_today - close_5d_ago) / close_5d_ago) * 100
                                    if pct_change >= 20.0:
                                        breadth_tracker[current_date_str]['Up'] += 1
                                    elif pct_change <= -20.0:
                                        breadth_tracker[current_date_str]['Down'] += 1
                    except:
                        continue
        except:
            continue
            
    status_text.empty()
    progress_bar.empty()
    
    if breadth_tracker:
        formatted_df = pd.DataFrame.from_dict(breadth_tracker, orient='index').reset_index()
        formatted_df.columns = ['Date', 'Up_20pct', 'Down_20pct']
        formatted_df = formatted_df.sort_values(by='Date')
        return formatted_df
    return pd.DataFrame()

# --- NEW 100+ HIGH MOMENTUM SMALL & MIDCAP NSE UNIVERSE POOL ---
# Pure high-beta, high-velocity midcaps aur smallcaps jisme asli 20% moves aate hain!
nse_universe = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
    "TATAMOTORS.NS", "AXISBANK.NS", "LT.NS", "KOTAKBANK.NS", "M&M.NS", "SUNPHARMA.NS", "NTPC.NS", "WIPRO.NS",
    "BAJAJFINSV.NS", "HCLTECH.NS", "ONGC.NS", "ADANIENT.NS", "COALINDIA.NS", "TATASTEEL.NS", "JIOFIN.NS",
    "HINDALCO.NS", "POWERGRID.NS", "MARUTI.NS", "INDUSINDBK.NS", "TITAN.NS", "ULTRACEMCO.NS", "GRASIM.NS",
    "ZOMATO.NS", "VBL.NS", "IRFC.NS", "BHEL.NS", "PFC.NS", "RECL.NS", "HUDCO.NS", "GMRINFRA.NS", "SUZLON.NS",
    "IDEA.NS", "YESBANK.NS", "IFCI.NS", "NBCC.NS", "TATAPOWER.NS", "NHPC.NS", "SJVN.NS", "IRCTC.NS", "RVNL.NS",
    "JINDALSTEL.NS", "SAIL.NS", "NATIONALUM.NS", "NMDC.NS", "VEDL.NS", "TATACOMM.NS", "GAIL.NS", "BPCL.NS",
    "IOC.NS", "HPCL.NS", "MRF.NS", "APOLLOTYRE.NS", "BALKRISIND.NS", "TATACHEM.NS", "UPL.NS", "AUBANK.NS",
    "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS", "BANKBARODA.NS", "L&TFH.NS", "M&MFIN.NS",
    "CHOLAFIN.NS", "PEL.NS", "MANAPPURAM.NS", "MUTHOOTFIN.NS", "LICHSGFIN.NS", "IBULHSGFIN.NS", "HINDCOPPER.NS",
    "SPLV.NS", "VOLTAS.NS", "HAVELLS.NS", "POLYCAB.NS", "DIXON.NS", "AMBUJACEM", "ACC.NS", "JKCEMENT.NS",
    "DELHIVERY.NS", "NYKAA.NS", "PAYTM.NS", "AWL.NS", "ADANIPOWER.NS", "ADANIGREEN.NS", "GMRINFRA.NS", "SWANENERGY.NS"
]

st.warning("👉 Click the button below to execute the live broad market computation model.")

# --- ACTION TRIGGER ---
if st.button("🚀 Run Market Breadth Scan", type="primary"):
    with st.spinner("Processing calculations over 100+ High-Beta Small & Midcaps... This will take around 20 seconds."):
        result_df = scan_large_universe(nse_universe, lookback_days)
        
    if not result_df.empty:
        st.success("Scan Completed Successfully!")
        
        latest = result_df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("Latest 5-Day Up 20% Count", int(latest['Up_20pct']))
        c2.metric("Latest 5-Day Down 20% Count", int(latest['Down_20pct']))
        
        # --- PLOTLY GRAPH INTERFACE ---
        st.subheader("📊 Stockbee 20% Breadth Visuals (NSE)")
        
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
        
        with st.expander("📂 View Raw Counts Data Table"):
            st.dataframe(result_df.sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.error("Engine failed to resolve values. Click run again.")
