import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Salman Mega Scanner", layout="wide")

st.title("🦅 رادار سلمان الشامل")

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    market = st.selectbox("السوق", ["S&P 500", "Nasdaq 100", "NYSE Top"])
    min_p = st.number_input("أقل سعر ($)", value=1.0)
    min_v = st.number_input("أقل سيولة", value=500000)
    sort_by = st.selectbox("ترتيب حسب:", ["1m %", "5m %", "Day %"])
    refresh_rate = st.slider("تحديث (ثانية)", 30, 300, 60)

# --- محرك البيانات ---
def get_data():
    if market == "S&P 500":
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tickers = pd.read_html(url)[0]['Symbol'].tolist()
    else:
        tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "AMZN", "META", "GOOGL"]
    
    tickers = [t.replace('.', '-') for t in tickers[:50]] 
    results = []
    for symbol in tickers:
        try:
            s = yf.Ticker(symbol)
            df_h = s.history(period="7d")
            df_i = s.history(period="1d", interval="1m")
            if df_h.empty or df_i.empty: continue
            
            p = df_i['Close'].iloc[-1]
            v = df_h['Volume'].iloc[-1]
            if p >= min_p and v >= min_v:
                results.append({
                    "Symbol": symbol,
                    "Price": round(float(p), 2),
                    "1m %": round(((p - df_i['Close'].iloc[-2]) / df_i['Close'].iloc[-2]) * 100, 2),
                    "5m %": round(((p - df_i['Close'].iloc[-6]) / df_i['Close'].iloc[-6]) * 100, 2),
                    "Day %": round(((p - df_h['Close'].iloc[-2]) / df_h['Close'].iloc[-2]) * 100, 2)
                })
        except: continue
    return pd.DataFrame(results)

# --- العرض ---
placeholder = st.empty()
while True:
    with placeholder.container():
        df = get_data()
        if not df.empty:
            st.write(f"✅ تحديث: {datetime.now().strftime('%H:%M:%S')}")
            st.dataframe(df.sort_values(by=sort_by, ascending=False), use_container_width=True)
    time.sleep(refresh_rate)
