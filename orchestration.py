# orchestration.py
from dagster import (
    asset,
    AssetExecutionContext,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
)
import pandas as pd
from pathlib import Path
from datetime import datetime

# Import your existing modular ETL logic
from etl.data_ingestion import extract
from etl.clean_data import deep_clean
from etl.data_transformation import filters
from persistence.database_engine import save_to_db

extracted_data_path = Path.cwd() / "stock_data.parquet"

@asset(description="Ingests raw parquet stock price data from the data lake/folder.")
def raw_stock_data(context: AssetExecutionContext) -> pd.DataFrame:
    months = 1
    if not extracted_data_path.exists():
        months = 12
        
    extract(datetime.now(), months)
    df= pd.read_parquet(extracted_data_path, engine="pyarrow")
    context.log.info(f"Ingested {len(df)} rows of raw stock data.")
    return df


@asset(description="Cleans stock data and flattens column hierarchies to level 1.")
def cleaned_stock_data(context: AssetExecutionContext, raw_stock_data: pd.DataFrame) -> pd.DataFrame:
    df = deep_clean(raw_stock_data)
    context.log.info(f"Cleaned data: {len(df)} rows across {df['ticker'].nunique()} tickers.")
    return df


@asset(description="Calculates technical indicators: MA cross, RSI, ADX, ATR, VWAP, HTF EMA.")
def feature_stock_data(context: AssetExecutionContext, cleaned_stock_data: pd.DataFrame) -> pd.DataFrame:
    transform = filters(cleaned_stock_data)
    df = transform.get_all_filters()
    context.log.info(f"Transformed indicators for {len(df)} rows.")
    return df


@asset(description="Upserts final long-format records into PostgreSQL stock_prices table.")
def persisted_stock_prices(context: AssetExecutionContext, feature_stock_data: pd.DataFrame) -> None:
    save_to_db(feature_stock_data)
    context.log.info("Successfully upserted data to PostgreSQL.")


# Define a job that materializes the full lineage
stock_pipeline_job = define_asset_job(
    name="daily_stock_pipeline_job",
    selection=[raw_stock_data, cleaned_stock_data, feature_stock_data, persisted_stock_prices],
)

# Schedule: Run Monday through Friday at 18:00 (6:00 PM) after market close
stock_pipeline_schedule = ScheduleDefinition(
    job=stock_pipeline_job,
    cron_schedule="0 18 * * 1-5",
    name="weekday_market_close_schedule",
)

# Bundle assets, jobs, and schedules into Definitions
defs = Definitions(
    assets=[raw_stock_data, cleaned_stock_data, feature_stock_data, persisted_stock_prices],
    schedules=[stock_pipeline_schedule],
)