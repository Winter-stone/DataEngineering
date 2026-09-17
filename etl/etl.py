import pandas as pd
from pathlib import Path
import etl.clean_data as cd
import etl.data_transformation as dt
from etl.data_ingestion import extract
from persistence.database_engine import save_to_db

from datetime import datetime

extrcted_data_path = Path.cwd() / "stock_data.parquet"

def run_pipeline():
    extract_data()
    data = clean_and_transform_data()
    save_to_db(data)
       
def extract_data():
    months = 1
    if not extrcted_data_path.exists():
        months = 12
    extract(datetime.now(), months)
        
def clean_and_transform_data():
    
    data = pd.read_parquet(extrcted_data_path, engine="pyarrow")
    data = cd.deep_clean(data)

    filters = dt.filters(data)
    data = filters.get_all_filters()

    data = cd.deep_clean(data)
    
    return data
