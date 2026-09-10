import pandas as pd

data = pd.read_parquet("stock_data.parquet", engine="pyarrow")

print(data.head())

print(data.info())