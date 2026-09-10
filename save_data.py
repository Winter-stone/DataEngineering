import pandas as pd
from sqlalchemy import create_engine

data = pd.read_parquet("stock_data.parquet", engine="pyarrow")

print(data.head())

print(data.info())