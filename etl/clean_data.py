import pandas as pd

def deep_clean(data):
    # Flattening the multi-index columns
    if isinstance(data.columns, pd.MultiIndex):
        data = data.stack(level=1, future_stack=True).reset_index()
        data.rename(columns={'level_1': 'ticker', "Open": "open", "Close": "close","Ticker":"ticker",
                             "High":"high", "Low":"low", "Volume":"volume", "Date":"date"}, inplace=True)
    
    # Check for missing values in the data
    if data.isnull().sum().any():
        data = data.dropna(inplace=True)
        
    # Check for duplicates in the data
    if data.duplicated().any():
         data = data[~data.duplicated(subset=["ticker", "date"], keep="first")]
         
    # Type casting for the columns and converting date into pandas datetime format
    data["date"] = pd.to_datetime(data["date"])
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        
    valid_mask = (
        (data["open"] > 0) &
        (data["high"] > 0) &
        (data["low"] > 0) &
        (data["close"] > 0) &
        (data["high"] >= data["low"]) &
        (data["high"] >= data["open"]) &
        (data["high"] >= data["close"]) &
        (data["low"] <= data["open"]) &
        (data["low"] <= data["close"]) &
        (data["volume"] >= 0)
    )
    data_cleaned = data[valid_mask].copy()

    # 7. Sort Chronologically
    data_cleaned.sort_values(by="date", inplace=True)
        
    return data_cleaned
