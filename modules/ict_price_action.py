import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# دریافت داده‌ها از yfinance
def fetch_data(symbol, timeframe="1h", start_date=None, end_date=None, limit=500):
    interval_map = {
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1wk"
    }
    interval = interval_map.get(timeframe, "1h")
    
    try:
        data = yf.download(tickers=symbol, start=start_date, end=end_date, interval=interval)
        if data.empty:
            raise ValueError(f"No data fetched for symbol: {symbol}")
        
        # تبدیل ایندکس تاریخ به ستون و تغییر نام
        data.reset_index(inplace=True)
        data.rename(columns={"Date": "Date"}, inplace=True)
        
        # تبدیل ستون‌ها به نوع عددی (float)
        data['High'] = pd.to_numeric(data['High'], errors='coerce')
        data['Low'] = pd.to_numeric(data['Low'], errors='coerce')
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        data = data.dropna(subset=['High', 'Low', 'Close'])
        
        data = data.tail(limit)
        return data
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# شناسایی BOS (Break of Structure)
def detect_bos(data, window=3):
    bos_signals = []
    for i in range(window, len(data) - window):
        prev_highs = data.iloc[i - window:i]['High']
        prev_lows = data.iloc[i - window:i]['Low']
        
        if data.iloc[i]['High'] > max(prev_highs):
            bos_signals.append({
                "time": str(data.iloc[i]['Date']),
                "price": data.iloc[i]['High'],
                "type": "BOS-UP"
            })
        
        if data.iloc[i]['Low'] < min(prev_lows):
            bos_signals.append({
                "time": str(data.iloc[i]['Date']),
                "price": data.iloc[i]['Low'],
                "type": "BOS-DOWN"
            })
    
    return bos_signals

# شناسایی FVG (Fair Value Gap)
def detect_fvg(data):
    fvg_zones = []
    for i in range(2, len(data)):
        body1 = [data.iloc[i - 2]['Low'], data.iloc[i - 2]['High']]
        body3 = [data.iloc[i]['Low'], data.iloc[i]['High']]
        
        if body1[1] < body3[0]:  # Gap up
            fvg_zones.append({
                "time": str(data.iloc[i]['Date']),
                "low": body1[1],
                "high": body3[0],
                "type": "FVG-UP"
            })
        
        if body3[1] < body1[0]:  # Gap down
            fvg_zones.append({
                "time": str(data.iloc[i]['Date']),
                "low": body3[1],
                "high": body1[0],
                "type": "FVG-DOWN"
            })
    
    return fvg_zones

# رسم نمودار برای نمایش تحلیل‌ها
def plot_ict_chart(data, bos, fvg):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(data['Date'], data['Close'], label="Close Price", color='black')
    
    # رسم سیگنال‌های BOS
    for signal in bos:
        color = 'green' if signal['type'] == 'BOS-UP' else 'red'
        ax.scatter(pd.to_datetime(signal['time']), signal['price'], color=color, marker='^' if color=='green' else 'v', s=100)
    
    # رسم نواحی FVG
    for zone in fvg:
        ax.axhspan(zone['low'], zone['high'], alpha=0.2, color='orange')

    ax.set_title("ICT Price Action Signals")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

# تحلیل ICT Price Action
def analyze_ict_price_action(symbol, tf="1h", start="2023-01-01", end="2024-01-01"):
    data = fetch_data(symbol, timeframe=tf, start_date=start, end_date=end)
    if data.empty:
        raise ValueError("No data fetched for symbol: {}".format(symbol))
    
    bos = detect_bos(data)
    fvg = detect_fvg(data)
    
    chart = plot_ict_chart(data, bos, fvg)
    return bos, fvg, chart
