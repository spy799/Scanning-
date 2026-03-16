import streamlit as st
import yfinance as yf
import pandas as pd
import time

# إعداد واجهة المستخدم
st.set_page_config(page_title="Radar Salman Al-Shaml", layout="wide")
st.title("🚀 Radar Salman Al-Shaml")

# القائمة الجانبية للإعدادات
st.sidebar.header("إعدادات الفلترة")
market_choice = st.sidebar.selectbox("اختر السوق", ["S&P 500", "Nasdaq 100"])
min_price = st.sidebar.number_input("أقل سعر للسهم ($)", value=10.0, step=1.0)
min_volume = st.sidebar.number_input("أقل حجم تداول (Volume)", value=1000000, step=50000)
refresh_rate = st.sidebar.slider("سرعة التحديث (بالثواني)", 10, 60, 30)

# دالة جلب القوائم
def get_tickers(market):
    if market == "S&P 500":
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
                    return pd.read_html(url)[0]['Symbol'].tolist()
                        else:
                                url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
                                        return pd.read_html(url)[4]['Ticker'].tolist()

                                        def get_data():
                                            tickers = get_tickers(market_choice)
                                                tickers = [t.replace('.', '-') for t in tickers]
                                                    results = []
                                                        
                                                            progress_bar = st.progress(0)
                                                                st.write(f"🔍 جاري فحص {len(tickers)} سهم...")
                                                                    
                                                                        for i, ticker in enumerate(tickers[:100]): # فحص أول 100 سهم للتجربة وسرعة الأداء
                                                                                try:
                                                                                            stock = yf.Ticker(ticker)
                                                                                                        hist = stock.history(period="2d", interval="1m")
                                                                                                                    
                                                                                                                                if hist.empty or len(hist) < 2:
                                                                                                                                                continue

                                                                                                                                                            current_price = hist['Close'].iloc[-1]
                                                                                                                                                                        volume = hist['Volume'].sum()

                                                                                                                                                                                    if current_price < min_price or volume < min_volume:
                                                                                                                                                                                                    continue

                                                                                                                                                                                                                # حساب النسب
                                                                                                                                                                                                                            c_1m = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                                                                                                                                                                                                                                        c_5m = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else 0
                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                results.append({
                                                                                                                                                                                                                                                                                "Ticker": ticker,
                                                                                                                                                                                                                                                                                                "Price": round(current_price, 2),
                                                                                                                                                                                                                                                                                                                "Volume": volume,
                                                                                                                                                                                                                                                                                                                                "1m %": round(c_1m, 2),
                                                                                                                                                                                                                                                                                                                                                "5m %": round(c_5m, 2)
                                                                                                                                                                                                                                                                                                                                                            })
                                                                                                                                                                                                                                                                                                                                                                    except:
                                                                                                                                                                                                                                                                                                                                                                                continue
                                                                                                                                                                                                                                                                                                                                                                                        progress_bar.progress((i + 1) / 100)
                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                return pd.DataFrame(results)

                                                                                                                                                                                                                                                                                                                                                                                                # التنفيذ
                                                                                                                                                                                                                                                                                                                                                                                                df = get_data()

                                                                                                                                                                                                                                                                                                                                                                                                if not df.empty:
                                                                                                                                                                                                                                                                                                                                                                                                    st.dataframe(df.sort_values(by="1m %", ascending=False))
                                                                                                                                                                                                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                                                                                                                                                                                                        st.warning("لا توجد نتائج، جرب تقليل شروط السعر والسيولة.")

                                                                                                                                                                                                                                                                                                                                                                                                        time.sleep(refresh_rate)
                                                                                                                                                                                                                                                                                                                                                                                                        st.rerun()
                                                                                                                                                                                                                                                                                                                                                                                                        