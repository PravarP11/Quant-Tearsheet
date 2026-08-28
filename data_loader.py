from datetime import timedelta
import pandas as pd
import numpy as np
import io
import streamlit as st
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

  df = user_input(raw_text)
  indexed_df = set_datetime_index(df)

  if len(indexed_df) > len(indexed_df.index.normalize().unique()):
    indexed_df = indexed_df.resample("1D").last().dropna()

  log_returns = calc_log_returns(indexed_df)
  return log_returns



BENCHMARK_TICKERS = {
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Nasdaq Crypto Index": "HASH11.SA",
}

@st.cache_data(ttl="6h", show_spinner=False)
def fetch_benchmark_returns(
    start_date: str, end_date: str, benchmark_name: str = "Nifty 50"
) -> pd.Series:
  """Fetches benchmark historical close prices with caching to prevent Yahoo Finance rate-limiting."""
  ticker = BENCHMARK_TICKERS.get(benchmark_name, "^NSEI")

  # Add 7-day padding around the date window
  dt_start = (pd.to_datetime(start_date) - pd.Timedelta(days=7)).strftime(
      "%Y-%m-%d"
  )
  dt_end = (pd.to_datetime(end_date) + pd.Timedelta(days=7)).strftime(
      "%Y-%m-%d"
  )

  try:
    df = yf.download(
        ticker,
        start=dt_start,
        end=dt_end,
        progress=False,
        auto_adjust=True,
    )

    if df is None or df.empty:
      return pd.Series(dtype=float, name="benchmark_returns")

    # Extract Close series reliably across single or multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
      if "Close" in df.columns.levels[0]:
        prices = df["Close"].iloc[:, 0]
      else:
        prices = df.iloc[:, 0]
    else:
      prices = df["Close"] if "Close" in df else df.iloc[:, 0]

    prices = prices.dropna().astype(float)
    if len(prices) < 2:
      return pd.Series(dtype=float, name="benchmark_returns")

    # Daily log returns
    bench_log_returns = np.log(prices / prices.shift(1)).dropna()
    bench_log_returns.name = "benchmark_returns"

    # Strip timezones
    if bench_log_returns.index.tz is not None:
      bench_log_returns.index = bench_log_returns.index.tz_convert(None)
    else:
      bench_log_returns.index = bench_log_returns.index.tz_localize(None)

    # Normalize to midnight timestamps
    bench_log_returns.index = pd.to_datetime(bench_log_returns.index.date)
    return bench_log_returns

  except Exception as e:
    print(f"Error downloading {benchmark_name}: {e}")
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