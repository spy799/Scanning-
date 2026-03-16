import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests

# إعدادات الصفحة - رادار سلمان الشامل
st.set_page_config(page_title="Salman Mega Scanner", layout="wide")

st.title("🦅 رادار سلمان الشامل")

# --- القائمة الجانبية (نفس طلباتك) ---
with st.sidebar:
    st.header("⚙️ إعدادات الرادار")
    market = st.selectbox("اختر السوق", ["S&P 500", "Nasdaq 100", "الأسهم القيادية"])
    min_p = st.number_input("أقل سعر للسهم ($)", value=1.0)
    min_v = st.number_input("أقل حجم تداول (Volume)", value=500000)
    sort_by = st.selectbox("ترتيب النتائج حسب:", ["1m %", "5m %", "Day %"])
    refresh_rate = st.slider("سرعة تحديث الرادار (ثانية)", 30, 300, 60)

# --- وظيفة جلب قائمة الأسهم (معالجة خطأ الصورة) ---
def get_tickers():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if market == "S&P 500":
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            res = requests.get(url, headers=headers)
            return pd.read_html(res.text)[0]['Symbol'].tolist()[:60]
        elif market == "Nasdaq 100":
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            res = requests.get(url, headers=headers)
            return pd.read_html(res.text)[4]['Ticker'].tolist()[:60]
        else:
            return ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "AMZN", "META", "GOOGL", "NFLX", "PYPL"]
    except:
        # قائمة طوارئ في حال تعطل موقع ويكيبيديا لضمان استمرار البحث
        return ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "AMZN", "META", "GOOGL"]

# --- محرك البحث والتحليل اللحظي ---
def run_scanner():
    ticker_list = get_tickers()
    results = []
    
    for symbol in ticker_list:
        try:
            symbol = symbol.replace('.', '-')
            s = yf.Ticker(symbol)
            
            # جلب البيانات اللحظية (فريم الدقيقة)
            df_live = s.history(period="2d", interval="1m")
            if df_live.empty: continue
            
            curr_p = df_live['Close'].iloc[-1]
            vol = df_live['Volume'].iloc[-1]
            
            # الفلترة حسب شروطك
            if curr_p >= min_p and vol >= min_v:
                # حساب نسب التغير المطلوبة
                c_1m = ((curr_p - df_live['Close'].iloc[-2]) / df_live['Close'].iloc[-2]) * 100
                c_5m = ((curr_p - df_live['Close'].iloc[-6]) / df_live['Close'].iloc[-6]) * 100 if len(df_live) > 5 else 0
                
                # جلب بيانات يومية لحساب تغير اليوم
                df_day = s.history(period="2d")
                c_day = ((curr_p - df_day['Close'].iloc[-2]) / df_day['Close'].iloc[-2]) * 100 if len(df_day) > 1 else 0
                
                results.append({
                    "Symbol": symbol,
                    "Price": round(float(curr_p), 2),
                    "1m %": round(float(c_1m), 2),
                    "5m %": round(float(c_5m), 2),
                    "Day %": round(float(c_day), 2),
                    "Volume": int(vol)
                })
        except: continue
    return pd.DataFrame(results)

# --- تشغيل العرض المباشر ---
placeholder = st.empty()
while True:
    with placeholder.container():
        data = run_scanner()
        if not data.empty:
            st.write(f"✅ تحديث الرادار: {datetime.now().strftime('%H:%M:%S')}")
            # الترتيب حسب اختيارك
            data = data.sort_values(by=sort_by, ascending=False)
            
            # عرض الجدول مع تلوين النسب (أخضر للصعود، أحمر للهبوط)
            st.dataframe(
                data.style.background_gradient(cmap='RdYlGn', subset=["1m %", "5m %", "Day %"]),
                use_container_width=True
            )
        else:
            st.info("جاري البحث عن فرص تطابق شروطك... تأكد من افتتاح السوق الأمريكي (5:30 م).")
            
    time.sleep(refresh_rate)
