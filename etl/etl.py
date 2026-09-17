import pandas as pd
import clean_data as cd
import data_transformation as dt

data = pd.read_parquet("stock_data.parquet", engine="pyarrow")
data = cd.deep_clean(data)

filters = dt.filters(data)

data = filters.get_all_filters()

data = cd.deep_clean(data)


print(data.head())

