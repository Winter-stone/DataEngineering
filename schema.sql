CREATE TABLE IF NOT EXISTS stock_prices (
    ticker VARCHAR(10) NOT NULL,
    date TIMESTAMP NOT NULL,
    open NUMERIC(12, 4) NOT NULL,
    high NUMERIC(12, 4) NOT NULL,
    low NUMERIC(12, 4) NOT NULL,
    close NUMERIC(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    ma_cross NUMERIC(12, 4) NOT NULL,
    mean_reversion NUMERIC(12, 4) NOT NULL,
    relative_volume NUMERIC(12, 4) NOT NULL,
    adx NUMERIC(12, 4) NOT NULL,
    atr NUMERIC(12, 4) NOT NULL,
    rsi NUMERIC(12, 4) NOT NULL,
    htf_ema NUMERIC(12, 4) NOT NULL,
    daily_vwap NUMERIC(12, 4) NOT NULL,
    PRIMARY KEY(ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_stock_ticker_time ON  stock_prices(ticker, date DESC);