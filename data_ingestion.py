import yfinance as yf
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Declare the date to download the ticker symbol data from the last 12 months
current_time = datetime.now()
start_time = (current_time - relativedelta(months=12)).strftime("%Y-%m-%d")
end_time = current_time.strftime("%Y-%m-%d")

# Declare the ticker symbol to download the data for
ticker_symbols = ["AAPL", "MSFT", "GOOGL", "SPY"]
# Download the data for the ticker symbol from Yahoo Finance

data = yf.download(ticker_symbols, start=start_time, end=end_time, auto_adjust=True)

data = data.stack(level=1, future_stack=True).reset_index()
data.rename(columns={'level_1': 'Ticker'}, inplace=True)
data["Date"] = pd.to_datetime(data["Date"])

# Flattening the multi-index columns and converting date into pandas datetime format
data.to_parquet("stock_data.parquet", engine="pyarrow", index=True)

print("data successfully downloaded and saved to stock_data.parquet")
