import streamlit as st
import traceback
from datetime import datetime
from modules.ict_price_action import analyze_ict_price_action

# پیکربندی اولیه صفحه
st.set_page_config(page_title="ICT Crypto Analyzer", layout="wide")
st.title("📊 ICT Price Action Analyzer")

# --- نوار کناری برای تنظیمات ---
st.sidebar.header("⚙️ Settings")

# انتخاب ارز دیجیتال
symbols = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "TON1141-USD"]
symbol = st.sidebar.selectbox("🔍 Select Cryptocurrency", symbols, index=0)

# انتخاب تایم‌فریم
tf_map = {
    "1h": "60m",
    "4h": "240m",
    "1d": "1d",
    "1w": "1wk"
}
timeframes = list(tf_map.keys())
selected_tf = st.sidebar.selectbox("⏰ Select Timeframe", timeframes, index=0)

# انتخاب بازه زمانی تحلیل
start_date = st.sidebar.date_input("📅 From Date", datetime(2023, 1, 1))
end_date = st.sidebar.date_input("📅 To Date", datetime.now())

# دکمه اجرا
run_analysis = st.sidebar.button("🚀 Run ICT Analysis")

# --- اجرای تحلیل ---
if run_analysis:
    st.subheader(f"📈 ICT Analysis for {symbol} | {selected_tf} timeframe")

    try:
        # اجرای تابع تحلیل ICT
        bos_list, fvg_list, chart = analyze_ict_price_action(
            symbol=symbol,
            tf=selected_tf,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )

        # نمایش BOS
        st.markdown("### 🔁 Break of Structure (BOS) Signals")
        if bos_list:
            for bos in bos_list[-5:]:
                st.markdown(f"- **{bos['type']}** | Time: {bos['time']} | Price: ${bos['price']:.2f}")
        else:
            st.info("No BOS signals found.")

        # نمایش FVG
        st.markdown("### 📉 Fair Value Gap (FVG) Zones")
        if fvg_list:
            for fvg in fvg_list[-5:]:
                st.markdown(f"- **{fvg['type']} FVG** | From ${fvg['low']:.2f} to ${fvg['high']:.2f} at {fvg['time']}")
        else:
            st.info("No FVG zones found.")

        # نمایش نمودار
        st.markdown("### 📊 Chart")
        st.pyplot(chart)

    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        st.code(traceback.format_exc())
