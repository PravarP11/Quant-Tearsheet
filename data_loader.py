import pandas as pd
import numpy as np
import io
import yfinance as yf


def user_input(raw_text: str) -> pd.DataFrame:
    #Takes raw data in csv format, turns it into an in-memory stream and loads it into 2-column dataframe

    text=raw_text.strip()

    if not text:
        raise ValueError("Error: Empty Data")

    csv_buffer = io.StringIO(text)
    df = pd.read_csv(csv_buffer)

    if df.shape[1]<2:
        raise ValueError("Error: Expected at least 2 cloumns (Data,Price)")
    
    return df

def set_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    #Takes DataFrame input, identifies Column 0 as the date, converts it to datetime object, sets it as index for row and sort it in latest order

    date_col = df.columns[0]
    copy_df = df.copy()

    copy_df[date_col] = pd.to_datetime(copy_df[date_col])

    copy_df = copy_df.set_index(date_col).sort_index()

    return copy_df

def calc_log_returns(df: pd.DataFrame) -> pd.Series:
    #Extracts the Price of each day and calculate the log returns: Ln(P_t)-Ln(P_(t-1))

    price_col = df.columns[0]
    prices = df[price_col].astype(float)

    log_prices = np.log(prices)

    log_returns = log_prices.diff()
    log_returns = log_returns.dropna()

    log_returns.name= "log_returns"

    return log_returns

def data_pipeline(raw_text: str) -> pd.Series:
    #Combines the 3 functions

    df = user_input(raw_text)
    indexed_df = set_datetime_index(df)
    log_returns = calc_log_returns(indexed_df)
    return log_returns



BENCHMARK_TICKERS = {
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bitcoin (Crypto Market Proxy)": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Nasdaq Crypto Index (Hashdex ETF)": "HASH11.SA",
}

def fetch_benchmark_returns(
    start_date: str, end_date: str, benchmark_name: str = "Nifty 50"
) -> pd.Series:
  """Fetches benchmark prices from Yahoo Finance and calculates daily log returns."""
  ticker = BENCHMARK_TICKERS.get(benchmark_name, "^NSEI")

  # Add 5-day padding before start and after end to prevent lost data points & exclusive end truncation
  dt_start = (pd.to_datetime(start_date) - pd.Timedelta(days=5)).strftime(
      "%Y-%m-%d"
  )
  dt_end = (pd.to_datetime(end_date) + pd.Timedelta(days=5)).strftime("%Y-%m-%d")

  try:
    data = yf.download(
        ticker,
        start=dt_start,
        end=dt_end,
        progress=False,
        auto_adjust=True,
    )

    if data.empty:
      return pd.Series(dtype=float, name="benchmark_returns")

    prices = data["Close"] if "Close" in data else data["Adj Close"]

    if isinstance(prices, pd.DataFrame):
      prices = prices.iloc[:, 0]

    prices = prices.dropna().astype(float)

    bench_log_returns = np.log(prices).diff().dropna()
    bench_log_returns.name = "benchmark_returns"

    # Safely strip timezone whether the index is tz-aware or tz-naive
    if bench_log_returns.index.tz is not None:
      bench_log_returns.index = bench_log_returns.index.tz_convert(None)
    else:
      bench_log_returns.index = bench_log_returns.index.tz_localize(None)

    # Normalize to date-only timestamps (00:00:00) to ensure clean inner joins
    bench_log_returns.index = pd.to_datetime(bench_log_returns.index.date)

    return bench_log_returns

  except Exception:
    return pd.Series(dtype=float, name="benchmark_returns")

def align_strategy_and_benchmark(
    strat_returns: pd.Series, bench_returns: pd.Series
) -> tuple[pd.Series, pd.Series]:
  """Aligns strategy and benchmark time series by matching mutual trading dates."""
  strat_df = strat_returns.to_frame(name="Strategy")
  bench_df = bench_returns.to_frame(name="Benchmark")

  # Standardize DatetimeIndex
  strat_df.index = pd.to_datetime(strat_df.index).tz_localize(None)
  bench_df.index = pd.to_datetime(bench_df.index).tz_localize(None)

  # Inner join to synchronize dates
  combined = pd.merge(
      strat_df, bench_df, left_index=True, right_index=True, how="inner"
  )

  return combined["Strategy"], combined["Benchmark"]