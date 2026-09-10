import yfinance as yf
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

data.to_parquet("stock_data.parquet", engine="pyarrow", index=True)

print("data successfully downloaded and saved to stock_data.parquet")
