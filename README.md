# Stock Market Data Engineering Pipeline
An end-to-end quantitative data engineering pipeline that ingests raw multi-ticker market data, cleans and flattens price structures, computes technical indicators, and idempotently persists long-format records into PostgreSQL. Orchestrated and scheduled via Dagster Software-Defined Assets.

# Architecture Overview
                      [ stock_data.parquet ]
                                │
                                ▼
                       [ raw_stock_data ]
                                │
                                ▼
                      [ cleaned_stock_data ]
                    (Level-1 Long-Format DF)
                                │
                                ▼
                     [ feature_stock_data ]
             (MA Cross, RSI, ADX, ATR, VWAP, HTF EMA)
                                │
                                ▼
                   [ persisted_stock_prices ]
                   (PostgreSQL Atomic Upsert)

### The pipeline handles:

Data Reshaping: Flattens multi-indexed column structures into a single-level long format with an independent ticker and date per row.

Feature Engineering: Calculates quantitative indicators across each ticker series without lookahead bias.

Database Idempotency: Loads records into a temporary staging table and uses PostgreSQL ON CONFLICT (ticker, date) DO NOTHING to prevent duplicate primary key violations on repeated runs.

Orchestration: Built using Dagster assets with built-in data lineage, parameter dependency injection, and cron-based market-close scheduling.

## Project Structure

# Plaintext
.
├── .env                       # Database credentials and local secrets
├── .gitignore                 # Python, environment, and OS ignore rules
├── README.md                  # Project documentation
├── schema.sql                 # PostgreSQL DDL table definition & indexes
├── stock_data.parquet         # Source market dataset
│
├── etl/
│   ├── __init__.py            # Package marker
│   ├── clean_data.py          # Column flattening & data cleaning
│   ├── data_ingestion.py      # Parquet reader & schema validation
│   ├── data_transformation.py # Indicator calculations (RSI, ADX, ATR, VWAP, EMA)
│   └── etl.py                 # Core procedural pipeline runner
│
├── persistence/
│   ├── __init__.py            # Package marker
│   └── database_engine.py     # SQLAlchemy engine, DDL executor & staging upsert
│
└── orchestration.py           # Dagster assets, jobs, and weekday schedule definitions

### Prerequisites & Installation
1. Requirements
Python 3.11 or 3.12

PostgreSQL 14+ installed and running locally or in Docker

2. Virtual Environment Setup
Bash
# Create environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source venv/bin/activate
3. Install Dependencies
Install the required data engineering, database, and orchestration packages:

Bash
pip install pandas pyarrow sqlalchemy psycopg2-binary python-dotenv dagster dagster-webserver
(Optional: If using high-performance columnar writes, install polars and adbc-driver-postgresql).

Configuration (.env)
Create a .env file in the project root:

LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=your_password_here
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=market_data
How to Run
Option A: Via Dagster Orchestration UI (Recommended)
To launch the asset catalog, view data lineage, and trigger scheduled runs:

Bash
dagster dev -f orchestration.py
Open your browser to http://127.0.0.1:3000.

Navigate to Assets to inspect the data pipeline graph.

Click "Materialize all" in the top-right corner to execute the end-to-end pipeline.

Go to Overview > Schedules to enable the automated market-close schedule (0 18 * * 1-5, Mon–Fri at 18:00).

Option B: Direct Python Execution (Standalone CLI)
To execute the ETL pipeline directly without the web UI:

Bash
python -m etl.etl