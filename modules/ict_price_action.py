import pandas as pd
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI

# اتصال به CoinGecko
cg = CoinGeckoAPI()

# تابع برای دریافت داده‌ها از CoinGecko
def fetch_data(symbol, start_date="2023-01-01", end_date="2023-07-01"):
    symbol_map = {
        "BTC-USD": "bitcoin",
        "ETH-USD": "ethereum",
        "XRP-USD": "ripple",
        "BNB-USD": "binancecoin",
        "SOL-USD": "solana",
        "ADA-USD": "cardano",
        "DOGE-USD": "dogecoin",
        "AVAX-USD": "avalanche-2",
        "DOT-USD": "polkadot",
        "TON1141-USD": "toncoin"
    }

    coin_id = symbol_map.get(symbol)
    if not coin_id:
        raise ValueError(f"Unsupported symbol: {symbol}")

    start_timestamp = int(pd.to_datetime(start_date).timestamp())
    end_timestamp = int(pd.to_datetime(end_date).timestamp())

    try:
        data = cg.get_coin_market_chart_range_by_id(id=coin_id, vs_currency='usd', from_timestamp=start_timestamp, to_timestamp=end_timestamp)

        if not data['prices']:
            raise ValueError(f"No data fetched for symbol: {symbol}")

        df = pd.DataFrame(data['prices'], columns=["Date", "Close"])
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')  # تبدیل به تاریخ
        df.set_index('Date', inplace=True)

        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# شناسایی Break of Structure (BOS)
def detect_bos(data, window=3):
    bos_signals = []
    for i in range(window, len(data) - window):
        prev_highs = data.iloc[i - window:i]['Close']
        prev_lows = data.iloc[i - window:i]['Close']

        if data.iloc[i]['Close'] > max(prev_highs):
            bos_signals.append({
                "time": str(data.iloc[i].name),
                "price": data.iloc[i]['Close'],
                "type": "BOS-UP",
                "action": "Buy"  # سیگنال خرید
            })

        if data.iloc[i]['Close'] < min(prev_lows):
            bos_signals.append({
                "time": str(data.iloc[i].name),
                "price": data.iloc[i]['Close'],
                "type": "BOS-DOWN",
                "action": "Sell"  # سیگنال فروش
            })
    
    return bos_signals

# شناسایی Fair Value Gap (FVG)
def detect_fvg(data):
    fvg_zones = []
    for i in range(2, len(data)):
        body1 = [data.iloc[i - 2]['Close'], data.iloc[i - 2]['Close']]
        body3 = [data.iloc[i]['Close'], data.iloc[i]['Close']]

        if body1[1] < body3[0]:  # Gap up
            fvg_zones.append({
                "time": str(data.iloc[i].name),
                "low": body1[1],
                "high": body3[0],
                "type": "FVG-UP",
                "action": "Buy"  # سیگنال خرید
            })

        if body3[1] < body1[0]:  # Gap down
            fvg_zones.append({
                "time": str(data.iloc[i].name),
                "low": body3[1],
                "high": body1[0],
                "type": "FVG-DOWN",
                "action": "Sell"  # سیگنال فروش
            })
    
    return fvg_zones

# رسم نمودار
def plot_ict_chart(data, bos, fvg):
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(data.index, data['Close'], label="Close Price", color='black')

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
def analyze_ict_price_action(symbol, tf="1d", start="2023-07-01", end="2023-12-31"):
    data = fetch_data(symbol, start_date=start, end_date=end)

    if data.empty:
        raise ValueError("No data fetched for symbol: {}".format(symbol))

    # شناسایی سیگنال‌های BOS و FVG
    bos = detect_bos(data)
    fvg = detect_fvg(data)
    
    # رسم نمودار
    chart = plot_ict_chart(data, bos, fvg)

    return bos, fvg, chart
