import pandas as pd
import persistance.save_data as sd
import etl.data_transformation as dt

data = pd.read_parquet("stock_data.parquet", engine="pyarrow")
data = sd.clean_data(data)

filters = dt.filters(data)

data = filters.get_all_filters()

data = sd.clean_data(data)


print(data.head())

