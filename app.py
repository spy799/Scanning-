import streamlit as st
from ib_insync import *
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import datetime

# إعداد واجهة المستخدم لتناسب شاشة الجوال واللابتوب
st.set_page_config(layout="wide", page_title="IBKR 4002 Scanner")

# تحديث تلقائي للجدول كل 30 ثانية (بدون تدخل منك)
st_autorefresh(interval=30000, key="ibkr_refresher")

st.title("📊 ماسح الأسهم الحقيقي (عبر Paper Gateway)")

def get_market_data():
    ib = IB()
    try:
        # الاتصال بالبورت 4002 كما حددت (Paper Gateway)
        ib.connect('127.0.0.1', 4002, clientId=1)
        
        # الفلترة المطلوبة: سعر > 1$ وحجم يومي > 500,000
        sub = ScannerSubscription(
            instrument='STK', 
            locationCode='STK.US.MAJOR', 
            scanCode='MOST_ACTIVE'
        )
        tag_values = [
            TagValue('avgVolumeAbove', '500000'),
            TagValue('priceAbove', '1')
        ]
        
        scan_results = ib.reqScannerData(sub, filterList=tag_values)
        # جلب أفضل 25 سهم لضمان سرعة التحديث كل 30 ثانية
        contracts = [res.contract for res in scan_results[:25]] 
        
        # الأطر الزمنية من 30 ثانية حتى 3 أشهر
        tfs = {
            '30s': '30 secs', '1m': '1 min', '5m': '5 mins', '15m': '15 mins',
            '30m': '30 mins', '1h': '1 hour', '2h': '2 hours', '4h': '4 hours',
            '1D': '1 day', '1W': '1 week', '1M': '1 month', '3M': '3 months'
        }
        
        rows = []
        for contract in contracts:
            ib.qualifyContracts(contract)
            row = {'Symbol': contract.symbol}
            for label, ib_tf in tfs.items():
                # جلب البيانات التاريخية لحساب آخر شمعة
                duration = '1 D'
                if 'week' in label: duration = '1 M'
                if 'month' in label: duration = '1 Y'
                
                bars = ib.reqHistoricalData(contract, '', duration, ib_tf, 'TRADES', False)
                if len(bars) >= 2:
                    change = ((bars[-1].close - bars[-2].close) / bars[-2].close) * 100
                    row[label] = round(change, 2)
                else:
                    row[label] = 0.0
            rows.append(row)
        
        ib.disconnect()
        return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame([{"خطأ": f"تأكد من فتح Gateway على بورت 4002: {e}"}])

# جلب البيانات
df = get_market_data()

# العرض التفاعلي
if not df.empty and "Symbol" in df.columns:
    # تنسيق الألوان (أخضر للصعود وأحمر للهبوط)
    st.dataframe(
        df.style.background_gradient(cmap='RdYlGn', axis=0, subset=df.columns[1:]), 
        use_container_width=True, 
        height=800
    )
    st.success(f"آخر تحديث: {datetime.datetime.now().strftime('%H:%M:%S')}")
else:
    st.error("لم يتم العثور على بيانات. تأكد من أن الأسواق مفتوحة أو اشتراكات البيانات مفعلة.")

st.sidebar.markdown(f"### 📱 للمتابعة من الجوال:\nادخل IP اللابتوب متبوعاً بـ `:8501` في المتصفح")
