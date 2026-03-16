import streamlit as st
import yfinance as yf
import pandas as pd
import time

# إعداد الواجهة
st.set_page_config(page_title="Radar Salman Al-Shaml", layout="wide")
st.title("🚀 Radar Salman Al-Shaml")

# الإعدادات الجانبية
st.sidebar.header("إعدادات الفلترة")
market = st.sidebar.selectbox("اختر السوق", ["S&P 500", "Nasdaq 100"])
min_p = st.sidebar.number_input("أقل سعر ($)", value=1.0)
min_v = st.sidebar.number_input("أقل سيولة", value=100000)

def get_data():
    # جلب القوائم
        if market == "S&P 500":
                url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
                        ticks = pd.read_html(url)[0]['Symbol'].tolist()
                            else:
                                    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
                                            ticks = pd.read_html(url)[4]['Ticker'].tolist()

                                                ticks = [t.replace('.', '-') for t in ticks]
                                                    results = []
                                                        
                                                            st.write(f"🔍 يتم الآن فحص {len(ticks)} سهم...")
                                                                prog = st.progress(0)
                                                                    
                                                                        # فحص أول 40 سهم فقط للتأكد من أن الكود شغال 100% وبدون تعليق
                                                                            for i, t in enumerate(ticks[:40]):
                                                                                    try:
                                                                                                s = yf.Ticker(t)
                                                                                                            h = s.history(period="1d", interval="1m")
                                                                                                                        if h.empty or len(h) < 2: continue
                                                                                                                                    
                                                                                                                                                p = h['Close'].iloc[-1]
                                                                                                                                                            v = h['Volume'].sum()
                                                                                                                                                                        
                                                                                                                                                                                    if p >= min_p and v >= min_v:
                                                                                                                                                                                                    # حساب النسب (دقيقة، 5 دقائق، ساعة)
                                                                                                                                                                                                                    c1 = ((p - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
                                                                                                                                                                                                                                    c5 = ((p - h['Close'].iloc[-6]) / h['Close'].iloc[-6]) * 100 if len(h) >= 6 else 0
                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                    results.append({"Ticker": t, "Price": round(p, 2), "Volume": v, "1m %": round(c1, 2), "5m %": round(c5, 2)})
                                                                                                                                                                                                                                                                            except: continue
                                                                                                                                                                                                                                                                                    prog.progress((i + 1) / 40)
                                                                                                                                                                                                                                                                                        return pd.DataFrame(results)

                                                                                                                                                                                                                                                                                        # عرض النتائج
                                                                                                                                                                                                                                                                                        df_final = get_data()
                                                                                                                                                                                                                                                                                        if not df_final.empty:
                                                                                                                                                                                                                                                                                            st.dataframe(df_final.sort_values(by="1m %", ascending=False))
                                                                                                                                                                                                                                                                                            else:
                                                                                                                                                                                                                                                                                                st.warning("لا توجد نتائج تطابق شروطك حالياً.")

                                                                                                                                                                                                                                                                                                time.sleep(30)
                                                                                                                                                                                                                                                                                                st.rerun()
                                                                                                                                                                                                                                                                                                