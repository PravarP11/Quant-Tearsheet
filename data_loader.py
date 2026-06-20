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
}

def fetch_benchmark_returns(start_date: str, end_date: str, benchmark_name: str = "Nifty 50") -> pd.Series:
  #Fetches benchmark prices from Yahoo Finance and calculates daily log returns.
  ticker = BENCHMARK_TICKERS.get(benchmark_name, "^NSEI")

  data = yf.download(ticker, start=start_date, end=end_date, progress=False)

  if data.empty:
    return pd.Series(dtype=float, name="benchmark_returns")

  prices = data["Close"] if "Close" in data else data["Adj Close"]

  if isinstance(prices, pd.DataFrame):
    prices = prices.iloc[:, 0]

  prices = prices.dropna().astype(float)

  bench_log_returns = np.log(prices).diff().dropna()
  bench_log_returns.name = "benchmark_returns"

  bench_log_returns.index = pd.to_datetime(bench_log_returns.index).tz_localize(
      None
  )
  return bench_log_returns

def align_strategy_and_benchmark(strategy_returns: pd.Series, benchmark_returns: pd.Series):
  #Aligns strategy and benchmark series to ensure they share the exact same dates

  strat_df = strategy_returns.to_frame(name="strategy")
  strat_df.index = pd.to_datetime(strat_df.index).date

  bench_df = benchmark_returns.to_frame(name="benchmark")
  bench_df.index = pd.to_datetime(bench_df.index).date

  merged = strat_df.join(bench_df, how="inner").dropna()
  merged.index = pd.to_datetime(merged.index)

  return merged["strategy"], merged["benchmark"] 