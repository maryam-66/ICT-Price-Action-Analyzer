import streamlit as st
from datetime import datetime
from modules.ict_price_action import analyze_ict_price_action

# پیکربندی اولیه صفحه
st.set_page_config(page_title="ICT Crypto Analyzer", layout="wide")

# عنوان صفحه
st.title("📊 ICT Price Action Analyzer")

# --- دیکشنری برای نگاشت نمادهای انتخابی به yfinance ---
yf_symbol_map = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "BNB": "BNB-USD",
    "SOL": "SOL-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "AVAX": "AVAX-USD",
    "DOT": "DOT-USD",
    "TON1141": "TON1141-USD"
}

# --- نوار کناری برای تنظیمات ---
st.sidebar.header("⚙️ Settings")

# انتخاب ارز دیجیتال
symbols = list(yf_symbol_map.keys())  # استفاده از کلیدهای دیکشنری برای انتخاب
symbol = st.sidebar.selectbox("🔍 Select Cryptocurrency", symbols, index=0)

# تبدیل نماد انتخابی به نماد yfinance
yf_symbol = yf_symbol_map.get(symbol)

# انتخاب تایم‌فریم
tf_map = {
    "1h": "60m",
    "4h": "240m",
    "1d": "1d",
    "1w": "1wk"
}
timeframes = list(tf_map.keys())
selected_tf = st.sidebar.selectbox("⏰ Select Timeframe", timeframes, index=timeframes.index("1d"))  # پیش‌فرض "1d"

# انتخاب بازه زمانی تحلیل
start_date = st.sidebar.date_input("📅 From Date", datetime(2025, 4, 1))  # از اول آوریل 2025
end_date = st.sidebar.date_input("📅 To Date", datetime.now())  # تاریخ امروز

# بررسی تاریخ شروع و پایان
if start_date > end_date:
    st.error("Start date cannot be later than end date.")
else:
    # دکمه اجرا
    run_analysis = st.sidebar.button("🚀 Run ICT Analysis")

    # --- اجرای تحلیل ---
    if run_analysis:
        st.subheader(f"📈 ICT Analysis for {symbol} | {selected_tf} timeframe")

        try:
            # اجرای تابع تحلیل ICT
            bos_list, fvg_list, chart = analyze_ict_price_action(
                symbol=yf_symbol,  # ارسال نماد yfinance به تابع تحلیل
                tf=selected_tf,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d")
            )

            # نمایش BOS
            st.markdown("### 🔁 Break of Structure (BOS) Signals")
            if bos_list:
                for bos in bos_list[-5:]:
                    # نمایش سیگنال‌های BOS و action آنها
                    st.markdown(f"- **{bos['type']}** | Date: {bos['time']} | Price: ${bos['price']:.2f} | Action: {bos.get('action', 'N/A')}")
            else:
                st.info("No BOS signals found.")

            # نمایش FVG
            st.markdown("### 📉 Fair Value Gap (FVG) Zones")
            if fvg_list:
                for fvg in fvg_list[-5:]:
                    # نمایش سیگنال‌های FVG و action آنها
                    st.markdown(f"- **{fvg['type']} FVG** | From ${fvg['low']:.2f} to ${fvg['high']:.2f} at {fvg['time']} | Action: {fvg.get('action', 'N/A')}")
            else:
                st.info("No FVG zones found.")

            # نمایش نمودار کندلی
            st.markdown("### 📊 Chart")
            st.pyplot(chart)

        except Exception as e:
            st.error(f"❌ Error during analysis: {e}")
