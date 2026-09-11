import pandas as pd
from sqlalchemy import create_engine

data = pd.read_parquet("stock_data.parquet", engine="pyarrow")

def clean_data(data):
    # Flattening the multi-index columns and converting date into pandas datetime format
    data = data.stack(level=1, future_stack=True).reset_index()
    data.rename(columns={'level_1': 'Ticker'}, inplace=True)
    data["Date"] = pd.to_datetime(data["Date"])
    
    # Check for missing values in the data
    if data.isnull().sum().any():
        data = data.dropna(inplace=True)
        
    # Check for duplicates in the data
    if data.duplicated().any():
         data = data[~data.duplicated(subset=["ticker", "date"], keep="first")]
         
    # 
        
    ...
    
data["RVOL"] = data.groupby("Ticker")["Volume"].transform(lambda x: x / x.rolling(window=20).mean()).fillna(0)
print(data.head())

print(data.info())

print("Check", any(data.duplicated()))
