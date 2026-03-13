import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Salman Pro Scanner", layout="wide")

st.title("📊 منصة سلمان لتحليل الأسهم اللحظية")

# --- الإعدادات في الشريط الجانبي ---
with st.sidebar:
    st.header("⚙️ التحكم")
        market = st.selectbox("السوق", ["S&P 500", "Nasdaq 100"])
            num_stocks = st.slider("عدد الأسهم", 50, 300, 100)
                btn_scan = st.button("🚀 ابدأ الفحص الآن")

                # --- دالة جلب البيانات ---
                def fetch_data():
                    if market == "S&P 500":
                            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
                                    tickers = pd.read_html(url)[0]['Symbol'].tolist()
                                        else:
                                                url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
                                                        tickers = pd.read_html(url)[4]['Ticker'].tolist()

                                                            tickers = [t.replace('.', '-') for t in tickers[:num_stocks]]
                                                                
                                                                    data_list = []
                                                                        for symbol in tickers:
                                                                                try:
                                                                                            s = yf.Ticker(symbol)
                                                                                                        hist_l = s.history(period="1mo")
                                                                                                                    hist_s = s.history(period="1d", interval="1m")
                                                                                                                                
                                                                                                                                            if hist_l.empty or hist_s.empty: continue
                                                                                                                                                        
                                                                                                                                                                    p = hist_l['Close'].iloc[-1]
                                                                                                                                                                                v = hist_l['Volume'].iloc[-1]
                                                                                                                                                                                            v_avg = hist_l['Volume'].mean()
                                                                                                                                                                                                        
                                                                                                                                                                                                                    data_list.append({
                                                                                                                                                                                                                                        "Symbol": symbol,
                                                                                                                                                                                                                                                        "Price": round(p, 2),
                                                                                                                                                                                                                                                                        "RVOL": round(v / v_avg, 2),
                                                                                                                                                                                                                                                                                        "1m%": round(((hist_s['Close'].iloc[-1]-hist_s['Close'].iloc[-2])/hist_s['Close'].iloc[-2]*100), 2),
                                                                                                                                                                                                                                                                                                        "Day%": round(((hist_l['Close'].iloc[-1]-hist_l['Close'].iloc[-2])/hist_l['Close'].iloc[-2]*100), 2)
                                                                                                                                                                                                                    })
                                                                                                                                                                                                                            except: continue
                                                                                                                                                                                                                                return pd.DataFrame(data_list)

                                                                                                                                                                                                                                # --- عرض النتائج ---
                                                                                                                                                                                                                                if btn_scan:
                                                                                                                                                                                                                                    df = fetch_data()
                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                            if not df.empty:
                                                                                                                                                                                                                                                    col1, col2 = st.columns([1, 2]) # تقسيم الشاشة لجدول وشارت
                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                    with col1:
                                                                                                                                                                                                                                                                                st.subheader("📋 قائمة الأسهم")
                                                                                                                                                                                                                                                                                            # اختيار السهم من القائمة لعرض الشارت الخاص به
                                                                                                                                                                                                                                                                                                        selected_symbol = st.selectbox("اختر سهم لرؤية الشارت", df['Symbol'].tolist())
                                                                                                                                                                                                                                                                                                                    st.dataframe(df.style.background_gradient(cmap='RdYlGn', subset=['1m%', 'Day%']), height=500)
                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                    with col2:
                                                                                                                                                                                                                                                                                                                                                st.subheader(f"📈 شارت دقيقة لـ {selected_symbol}")
                                                                                                                                                                                                                                                                                                                                                            chart_stock = yf.Ticker(selected_symbol)
                                                                                                                                                                                                                                                                                                                                                                        chart_df = chart_stock.history(period="1d", interval="1m")
                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                fig = go.Figure(data=[go.Candlestick(
                                                                                                                                                                                                                                                                                                                                                                                                                    x=chart_df.index,
                                                                                                                                                                                                                                                                                                                                                                                                                                    open=chart_df['Open'], high=chart_df['High'],
                                                                                                                                                                                                                                                                                                                                                                                                                                                    low=chart_df['Low'], close=chart_df['Close']
                                                                                                                                                                                                                                                                                                                                                                                                )])
                                                                                                                                                                                                                                                                                                                                                                                                            fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,b=0,t=0))
                                                                                                                                                                                                                                                                                                                                                                                                                        st.plotly_chart(fig, use_container_width=True)
                                                                                                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                )])
                                                                                                                                                                                                                    })