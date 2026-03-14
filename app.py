import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import streamlit.components.v1 as components

# إعداد الصفحة
st.set_page_config(page_title="Salman Ultra Scanner", layout="wide")

# --- دالة التنبيه الصوتي (تشتغل على الجوال) ---
def play_sound():
    sound_html = """
    <audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>
    """
    components.html(sound_html, height=0)

st.title("🦅 رادار سلمان - صائد الفرص الانفجارية")

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    market = st.selectbox("اختر السوق", ["S&P 500", "Nasdaq 100", "NYSE Top"])
    min_p = st.number_input("أقل سعر ($)", value=1.0)
    min_v = st.number_input("أقل سيولة", value=500000)
    num_assets = st.slider("عدد الأسهم", 20, 300, 100)
    sort_by = st.selectbox("رتب حسب الأكثر صعوداً في:", 
                          ["1m %", "5m %", "15m %", "30m %", "1h %", "4h %", "Day %", "Week %", "Month %", "3M %"])
    refresh_rate = st.slider("تحديث كل (ثانية)", 30, 300, 60)

# --- محرك التحليل الشامل ---
def get_mega_data():
    if market == "S&P 500":
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tickers = pd.read_html(url)[0]['Symbol'].tolist()
    elif market == "Nasdaq 100":
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        tickers = pd.read_html(url)[4]['Ticker'].tolist()
    else:
        tickers = ["BRK-B", "UNH", "V", "JPM", "MA", "WMT", "XOM", "LLY", "PG", "PFE", "BA", "KO", "DIS"]

    tickers = [t.replace('.', '-') for t in tickers[:num_assets]]
    results = []
    
    for symbol in tickers:
        try:
            s = yf.Ticker(symbol)
            df_hist = s.history(period="6mo") 
            df_intraday = s.history(period="2d", interval="1m")
            
            if df_hist.empty or df_intraday.empty: continue
            
            curr_p = df_intraday['Close'].iloc[-1]
            vol = df_hist['Volume'].iloc[-1]

            if curr_p < min_p or vol < min_v: continue

            def get_change(df, period_idx):
                try:
                    old_p = df['Close'].iloc[-period_idx]
                    return round(((curr_p - old_p) / old_p) * 100, 2)
                except: return 0.0

            results.append({
                "Symbol": symbol,
                "Price": round(float(curr_p), 2),
                "1m %": get_change(df_intraday, 2),
                "5m %": get_change(df_intraday, 6),
                "15m %": get_change(df_intraday, 16),
                "30m %": get_change(df_intraday, 31),
                "1h %": get_change(df_intraday, 61),
                "4h %": get_change(df_intraday, 241),
                "Day %": round(((curr_p - df_hist['Close'].iloc[-2]) / df_hist['Close'].iloc[-2]) * 100, 2),
                "Week %": round(((curr_p - df_hist['Close'].iloc[-6]) / df_hist['Close'].iloc[-6]) * 100, 2),
                "Month %": round(((curr_p - df_hist['Close'].iloc[-22]) / df_hist['Close'].iloc[-22]) * 100, 2),
                "3M %": round(((curr_p - df_hist['Close'].iloc[-64]) / df_hist['Close'].iloc[-64]) * 100, 2)
            })
        except: continue
    return pd.DataFrame(results)

# --- العرض والتنبيهات ---
placeholder = st.empty()

while True:
    with placeholder.container():
        df = get_mega_data()
        if not df.empty:
            st.write(f"✅ آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")
            df = df.sort_values(by=sort_by, ascending=False)
            
            # ميزة التنبيه للفرصة الذهبية (أخضر في كل شيء)
            golden = df[(df['1m %'] > 0) & (df['Day %'] > 0) & (df['Week %'] > 0)]
            if not golden.empty:
                play_sound()
                st.success(f"🔥 رصد فرصة ذهبية الآن في سهم: {golden.iloc[0]['Symbol']}")
                st.toast(f"فرصة ذهبية في {golden.iloc[0]['Symbol']}", icon="🚀")

            percentage_cols = ["1m %", "5m %", "15m %", "30m %", "1h %", "4h %", "Day %", "Week %", "Month %", "3M %"]
            st.dataframe(df.style.background_gradient(cmap='RdYlGn', subset=percentage_cols), use_container_width=True, height=600)
            
    time.sleep(refresh_rate)
