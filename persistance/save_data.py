import pandas as pd
from sqlalchemy import create_engine

def clean_data(data):
    # Flattening the multi-index columns
    if isinstance(data.columns, pd.MultiIndex):
        data = data.stack(level=1, future_stack=True).reset_index()
        data.rename(columns={'level_1': 'Ticker'}, inplace=True)
    
    # Check for missing values in the data
    if data.isnull().sum().any():
        data = data.dropna(inplace=True)
        
    # Check for duplicates in the data
    if data.duplicated().any():
         data = data[~data.duplicated(subset=["ticker", "date"], keep="first")]
         
    # Type casting for the columns and converting date into pandas datetime format
    data["Date"] = pd.to_datetime(data["Date"])
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        
    valid_mask = (
        (data["Open"] > 0) &
        (data["High"] > 0) &
        (data["Low"] > 0) &
        (data["Close"] > 0) &
        (data["High"] >= data["Low"]) &
        (data["High"] >= data["Open"]) &
        (data["High"] >= data["Close"]) &
        (data["Low"] <= data["Open"]) &
        (data["Low"] <= data["Close"]) &
        (data["Volume"] >= 0)
    )
    data_cleaned = data[valid_mask].copy()

    # 7. Sort Chronologically
    data_cleaned = data_cleaned.sort_values("Date").reset_index(drop=True)
        
    return data_cleaned
    
# data = clean_data(data)
