import pandas as pd
from pathlib import Path
import clean_data as cd
import data_transformation as dt
from data_ingestion import extract
from persistence.database_engine import save_to_db

from datetime import datetime

extrcted_data_path = Path.cwd().parent / "stock_data.parquet"

def extract_data():
    if not extrcted_data_path.exists():
        extract(datetime.now())
        
def clean_and_transform_data():
    
    data = pd.read_parquet(extrcted_data_path, engine="pyarrow")
    data = cd.deep_clean(data)

    filters = dt.filters(data)
    data = filters.get_all_filters()

    data = cd.deep_clean(data)
    
    return data

save_to_db(clean_and_transform_data())
