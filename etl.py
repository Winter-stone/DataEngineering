import pandas as pd
import save_data as sd
import data_transformation as dt

data = pd.read_parquet("stock_data.parquet", engine="pyarrow")
data = sd.clean_data(data)

filters = dt.filters(data)


data = filters.calculate_daily_vwap(data)
data = filters.calculate_rsi(data)
data = filters.calculate_adx(data)


print(data.head())

