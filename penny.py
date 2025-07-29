import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define screening criteria for penny stocks
PRICE_MAX = 5.00  # Max price for penny stocks
MIN_MARKET_CAP = 50e6  # Minimum market cap ($50M)
MAX_MARKET_CAP = 300e6  # Maximum market cap ($300M)
MIN_VOLUME = 200000  # Minimum 30-day avg volume
LOOKBACK_DAYS = 50  # Days for historical data

def fetch_stock_data(symbols):
    """Fetch stock data for a list of symbols."""
    stock_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=LOOKBACK_DAYS)
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty:
                continue
            
            # Get latest data
            latest = hist.iloc[-1]
            price = latest['Close']
            volume = hist['Volume'].mean()  # 30-day avg volume
            market_cap = stock.info.get('marketCap', 0)
            
            # Calculate moving averages
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            prev_ma20 = hist['Close'].rolling(window=20).mean().iloc[-2]
            prev_ma50 = hist['Close'].rolling(window=50).mean().iloc[-2]
            
            # Calculate 5-day price change
            price_change_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
            
            stock_data.append({
                'Symbol': symbol,
                'Price': price,
                'MarketCap': market_cap,
                'AvgVolume': volume,
                'MA20': ma20,
                'MA50': ma50,
                'PriceChange5D': price_change_5d,
                'BullishCrossover': ma20 > ma50 and prev_ma20 <= prev_ma50  # Golden cross
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    return pd.DataFrame(stock_data)

def screen_penny_stocks(symbols):
    """Screen penny stocks for bullish signals."""
    df = fetch_stock_data(symbols)
    
    # Apply filters
    filtered_df = df[
        (df['Price'] <= PRICE_MAX) &
        (df['MarketCap'].between(MIN_MARKET_CAP, MAX_MARKET_CAP)) &
        (df['AvgVolume'] >= MIN_VOLUME) &
        (df['PriceChange5D'] > 0) &  # Positive 5-day performance
        (df['BullishCrossover'] == True)  # Golden cross signal
    ]
    
    return filtered_df.sort_values(by='PriceChange5D', ascending=False)

def main():
    # Example list of penny stock symbols (replace with a comprehensive list or use an API)
    # For demo, using a small set from sources like Nasdaq and Timothy Sykes
    penny_stocks = [
        'ABCL', 'SLDB', 'SBET', 'OKLO', 'UEC', 'LUNR', 'SGMO', 'SVM', 'ACHR', 'BITF'
    ]
    
    print("Screening penny stocks for potential price increases...")
    results = screen_penny_stocks(penny_stocks)
    
    if results.empty:
        print("No penny stocks meet the criteria.")
    else:
        print("\nPenny Stocks with Bullish Signals (Potential for Price Increase):")
        print(results[['Symbol', 'Price', 'MarketCap', 'AvgVolume', 'PriceChange5D']].to_string(index=False))
        print("\nNote: These are not guaranteed to skyrocket. Conduct thorough research and consider risks.")

if __name__ == "__main__":
    main()