import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests

# إعداد الصفحة
st.set_page_config(page_title="Salman Mega Scanner", layout="wide")

st.title("🦅 رادار سلمان الشامل - وضع الفحص المستمر")

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    market = st.selectbox("السوق", ["S&P 500", "Nasdaq 100", "NYSE Top"])
    min_p = st.number_input("أقل سعر ($)", value=1.0)
    min_v = st.number_input("أقل سيولة", value=500000)
    sort_by = st.selectbox("ترتيب حسب:", ["Day %", "5m %", "15m %", "30m %", "1h %", "2h %", "4h %", "1D %", "1W %", "1m %"])
    refresh_rate = st.slider("تحديث (ثانية)", 30, 300, 60)

# --- محرك البيانات المطور للعمل وقت الإغلاق ---
def get_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if market == "S&P 500":
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url, headers=headers)
            tickers = pd.read_html(response.text)[0]['Symbol'].tolist()
        elif market == "Nasdaq 100":
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            response = requests.get(url, headers=headers)
            tickers = pd.read_html(response.text)[4]['Ticker'].tolist()
        else:
            tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "AMZN", "META", "GOOGL"]
        
        tickers = [t.replace('.', '-') for t in tickers[:50]] 
        results = []
        
        for symbol in tickers:
            try:
                s = yf.Ticker(symbol)
                # جلب بيانات 5 أيام لضمان وجود بيانات حتى لو السوق مغلق
                df_h = s.history(period="5d", interval="1m") if not s.history(period="1d", interval="1m").empty else s.history(period="5d")
                
                if df_h.empty: continue
                
                curr_p = df_h['Close'].iloc[-1]
                prev_p = df_h['Close'].iloc[-2]
                vol = df_h['Volume'].iloc[-1]
                
                if curr_p >= min_p and vol >= min_v:
                    results.append({
                        "Symbol": symbol,
                        "Price": round(float(curr_p), 2),
                        "1m %": round(((curr_p - df_h['Close'].iloc[-2]) / df_h['Close'].iloc[-2]) * 100, 4) if len(df_h) > 1 else 0,
                        "5m %": round(((curr_p - df_h['Close'].iloc[-6]) / df_h['Close'].iloc[-6]) * 100, 2) if len(df_h) > 5 else 0,
                        "Day %": round(((curr_p - prev_p) / prev_p) * 100, 2)
                    })
            except: continue
        return pd.DataFrame(results)
    except: return pd.DataFrame()

# --- العرض ---
placeholder = st.empty()
while True:
    with placeholder.container():
        df = get_data()
        if not df.empty:
            st.write(f"✅ حالة السوق: {'مغلق (بيانات تاريخية)' if datetime.now().weekday() >= 5 else 'مفتوح (بيانات لحظية)'}")
            st.write(f"⏰ توقيت الفحص: {datetime.now().strftime('%H:%M:%S')}")
            df = df.sort_values(by=sort_by, ascending=False)
            st.dataframe(df.style.background_gradient(cmap='RdYlGn', subset=["Day %"]), use_container_width=True)
        else:
            st.info("جاري محاولة الاتصال بالخادم وجلب البيانات... قد يستغرق ذلك دقيقة.")
    time.sleep(refresh_rate)
