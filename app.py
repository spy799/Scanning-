import streamlit as st
from ib_insync import *
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import asyncio

# القضاء على خطأ الـ Event Loop
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

st.set_page_config(layout="wide", page_title="Scanner 4002")
st_autorefresh(interval=30000, key="refresher")

st.title("📊 ماسح الأسهم الحقيقي - بورت 4002")

def get_data():
    ib = IB()
    # استخدام util.patch() ضروري جداً لتشغيل ib_insync داخل Streamlit
    util.patchAsyncio() 
    try:
        # الاتصال بـ Gateway بورت 4002
        ib.connect('127.0.0.1', 4002, clientId=1, timeout=10)
        
        sub = ScannerSubscription(instrument='STK', locationCode='STK.US.MAJOR', scanCode='MOST_ACTIVE')
        tag_values = [TagValue('avgVolumeAbove', '500000'), TagValue('priceAbove', '1')]
        
        scan_results = ib.reqScannerData(sub, filterList=tag_values)
        contracts = [res.contract for res in scan_results[:15]] 
        
        tfs = {'1m': '1 min', '5m': '5 mins', '1h': '1 hour', '1D': '1 day'}
        rows = []
        for contract in contracts:
            ib.qualifyContracts(contract)
            row = {'Symbol': contract.symbol}
            for label, ib_tf in tfs.items():
                bars = ib.reqHistoricalData(contract, '', '1 D', ib_tf, 'TRADES', False)
                if len(bars) >= 2:
                    change = ((bars[-1].close - bars[-2].close) / bars[-2].close) * 100
                    row[label] = round(change, 2)
                else: row[label] = 0.0
            rows.append(row)
        ib.disconnect()
        return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame([{"Error": f"الاتصال فشل: {e}"}])

df = get_data()
if not df.empty and "Symbol" in df.columns:
    st.dataframe(df.style.background_gradient(cmap='RdYlGn', axis=0), use_container_width=True)
else:
    st.write(df)
