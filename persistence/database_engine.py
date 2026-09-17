import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

env_file_path = Path.cwd() / ".env"

try:
    with open(env_file_path, "r") as file:
        password = file.readline().strip().split("=")[1]
        
except FileNotFoundError as e:
    print("File .env not found | create .env file in the main directory and store your password.")
    
DB_USER = "postgres"
DB_PASSWORD = password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "market_data"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
ADMIN_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"

admin_engine = create_engine(ADMIN_URL, isolation_level = "AUTOCOMMIT")
engine = create_engine(DATABASE_URL)

def check_if_db_exists():
    
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": DB_NAME}
        ).scalar()
        
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
            print(f"Created database: {DB_NAME}")
            create_schema()
        
def create_schema():
    sql_file_path = Path.cwd() / "schema.sql"
    with open(sql_file_path, "r", encoding = "utf-8") as file:
        ddl_statements = file.read()
        
    with engine.begin() as connection:
        connection.execute(text(ddl_statements))
        
    print(f"schema successfully applied to database '{DB_NAME}'!")
    
def save_to_db(df, table_name="stock_prices"):
    with engine.begin() as conn:
        # 1. Write the DataFrame to a temporary staging table
        # 'temporary=True' ensures Postgres drops it automatically if connection drops
        df.to_sql(
            name="temp_stock_staging",
            con=conn,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=5000
        )

        # 2. Perform atomic insert into real table, skipping existing ticker/timestamp rows
        upsert_query = text(f"""
            INSERT INTO {table_name} (
                ticker, date, open, high, low, close, volume, 
                ma_cross, mean_reversion, relative_volume, 
                adx, atr, rsi, htf_ema, daily_vwap
            )
            SELECT 
                ticker, date, open, high, low, close, volume, 
                ma_cross, mean_reversion, relative_volume, 
                adx, atr, rsi, htf_ema, daily_vwap
            FROM temp_stock_staging
            ON CONFLICT (ticker, date) 
            DO NOTHING;

            DROP TABLE IF EXISTS temp_stock_staging;
        """)

        conn.execute(upsert_query)
        
    
        print(f"data successfully saved to database '{DB_NAME}'!")
    
check_if_db_exists()