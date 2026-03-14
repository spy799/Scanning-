import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests

# إعدادات الصفحة
st.set_page_config(page_title="Salman Mega Scanner", layout="wide")

st.title("🦅 رادار سلمان الشامل")

# --- القائمة الجانبية لزيادة الربحية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    market = st.selectbox("السوق", ["S&P 500", "Nasdaq 100", "NYSE Top"])
    min_p = st.number_input("أقل سعر ($)", value=1.0)
    min_v = st.number_input("أقل سيولة", value=500000)
    sort_by = st.selectbox("ترتيب حسب:", ["1m %", "5m %", "Day %"])
    refresh_rate = st.slider("تحديث (ثانية)", 30, 300, 60)

# --- محرك البيانات المحدث لتجاوز الحظر ---
def get_data():
    # هوية متصفح وهمية لتجاوز حظر ويكيبيديا
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
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
            tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "AMZN", "META", "GOOGL", "NFLX", "PYPL"]
        
        tickers = [t.replace('.', '-') for t in tickers[:100]] # فحص أول 100 سهم لزيادة السرعة
        results = []
        
        for symbol in tickers:
            try:
                s = yf.Ticker(symbol)
                # جلب البيانات اللحظية والتاريخية
                df_h = s.history(period="7d")
                df_i = s.history(period="1d", interval="1m")
                
                if df_h.empty or df_i.empty: continue
                
                p = df_i['Close'].iloc[-1]
                v = df_h['Volume'].iloc[-1]
                
                # تطبيق شروط الربحية الخاصة بك
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
    except Exception as e:
        st.error(f"خطأ في جلب قائمة الأسهم: {e}")
        return pd.DataFrame()

# --- العرض والتحديث ---
placeholder = st.empty()
while True:
    with placeholder.container():
        df = get_data()
        if not df.empty:
            st.write(f"✅ تحديث السوق: {datetime.now().strftime('%H:%M:%S')}")
            # الترتيب التلقائي لاقتناص أقوى الفرص
            df = df.sort_values(by=sort_by, ascending=False)
            st.dataframe(df.style.background_gradient(cmap='RdYlGn', subset=["1m %", "5m %", "Day %"]), use_container_width=True)
        else:
            st.warning("جاري البحث عن أسهم تطابق الشروط...")
            
    time.sleep(refresh_rate)
