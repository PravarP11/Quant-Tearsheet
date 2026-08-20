import numpy as np
import pandas as pd

def cumulative_returns(log_returns: pd.Series) -> float:
    #Calculates total compound return over the entire period

    if log_returns.empty:
        return 0

    total_return = log_returns.sum()

    cumulative_return = (np.exp(total_return)-1).astype(float)

    return cumulative_return

def cagr_returns(log_return: pd.Series) -> float:
    #Calculates Compound Annual Growth Rate (CAGR)

    if log_return.empty or len(log_return)<2:
        return 0

    daily_mean_return = log_return.mean()

    annual_return = daily_mean_return * 252 #Trading days in a year

    cagr = (np.exp(annual_return)-1).astype(float)

    return cagr


def annual_volatility(log_returns: pd.Series) -> float:
    #Calculates Standard deviation of daily log returns and converts it into annual SD

    if log_returns.empty or len(log_returns)<2:
        return 0

    daily_vola = log_returns.std(ddof=1)
    annual_vola = (daily_vola * np.sqrt(252)).astype(float)

    return annual_vola

def downside_volatility(log_returns: pd.Series) -> float:
    #Calculates annual downside deviation (Risk of negative return below MAR)
    #MAR by default = 0

    if log_returns.empty or len(log_returns)<2:
            return 0

    downside_diff = log_returns[log_returns < 0] - 0

    if downside_diff.empty:
         return 0

    downside_daily = np.sqrt(np.mean(downside_diff **2))
    downside_vola = (downside_daily* np.sqrt(252)).astype(float)

    return downside_vola

def sharpe_ratio(cagr:float , annual_vola:float) -> float:
    #Calculates Sharpe ratio using ratio of CAGR and Annual Volatility

    if annual_vola == 0 or np.isnan(annual_vola):
        return 0

    return float(cagr/annual_vola)

def sortino_ratio(cagr:float , downside_vola: float) -> float:
    #Calculates sortino ratio using ratio of CAGR and Downside volatility

    if downside_vola ==0 or np.isnan(downside_vola):
        return 0

    return float(cagr/downside_vola)

def drawdown_series(log_returns: pd.Series) -> pd.Series:
    #Calculates the underwater curve (percentage drawdown)

    if log_returns.empty:
        return pd.Series(dtype=float)

    cumulative_wealth = np.exp(log_returns.cumsum())

    peak_mark = cumulative_wealth.cummax()

    drawdown = (cumulative_wealth - peak_mark)/peak_mark
    drawdown.name = "drawdown"
    return drawdown

def max_drawdown(drawdown_series: pd.Series) -> float:
    #Minimum value of the drawdown series
    return float(drawdown_series.min())

def calmar_ratio(cagr: float, max_drawdown: float) -> float:
    #Calculates the ratio of CAGR and MaxDrawdown
    if max_drawdown == 0 or np.isnan(max_drawdown):
        return 0
    return float(cagr/abs(max_drawdown))


def historical_var(log_returns: pd.Series, confidence_level: float =0.95)->float:
    #Calculates historaical daily Value at Risk(VaR) at 95% confidence.

    if log_returns.empty:
        return 0

    percentile_cutoff = (1-confidence_level)*100

    var_value = np.percentile(log_returns,percentile_cutoff)

    var_simple = 1 - np.exp(var_value) 
    return float(max(0,var_simple))

def conditional_var(log_returns: pd.Series, confidence_level: float = 0.95) -> float:
    #Calculates Average loss incurred on days that breach the VaR Threshold.

    if log_returns.empty:
            return 0

    percentile_cutoff = (1-confidence_level)*100
    cutoff_return = np.percentile(log_returns, percentile_cutoff)

    tail_losses = log_returns[log_returns <= cutoff_return]

    if tail_losses.empty:
        return 0.0

    cvar = tail_losses.mean()
    cvar_simple = 1 - np.exp(cvar)

    return float(max(0,cvar_simple))


def generate_metrics_summary(log_returns: pd.Series) -> dict:
    #Aggregates all performance parameters and returns a dictionary

    cum_ret = cumulative_returns(log_returns)
    cagr = cagr_returns(log_returns)

    annual_vola = annual_volatility(log_returns)
    down_vola = downside_volatility(log_returns)
    sharpe = sharpe_ratio(cagr, annual_vola)
    sortino = sortino_ratio(cagr, down_vola)

    dd_curve = drawdown_series(log_returns)
    max_dd = max_drawdown(dd_curve)
    calmar = calmar_ratio(cagr, max_dd)

    var_95 = historical_var(log_returns, confidence_level= 0.95)
    cvar_95 = conditional_var(log_returns, confidence_level=0.95)

    return {
        "Cumulative Return": cum_ret,
        "CAGR": cagr,
        "Annual Volatility": annual_vola,
        "Downside Volatility": down_vola,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Max Drawdown": max_dd,
        "Calmar Ratio": calmar,
        "Daily VaR (95%)": var_95,
        "Daily CVaR (95%)": cvar_95,
    }

def beta_and_alpha(strategy_returns: pd.Series, benchmark_returns: pd.Series, risk_free_rate: float = 0.0):
    #Calculates Beta (market sensitivity) and Annualized Jensen's Alpha.
  
    if len(strategy_returns) < 2 or len(benchmark_returns) < 2:
        return 0.0, 0.0

    covariance = np.cov(strategy_returns, benchmark_returns)[0, 1]
    
    bench_variance = np.var(benchmark_returns, ddof=1)

    if bench_variance == 0 or np.isnan(bench_variance):
        return 0.0, 0.0

    beta = float(covariance / bench_variance)

    strat_cagr = cagr_returns(strategy_returns)
    bench_cagr = cagr_returns(benchmark_returns)

    alpha = float((strat_cagr - risk_free_rate) - beta * (bench_cagr - risk_free_rate))

    return beta, alpha


def tracking_error_and_ir(strategy_returns: pd.Series, benchmark_returns: pd.Series):
    #Calculates Annualized Tracking Error and Information Ratio (IR).
  
    if len(strategy_returns) < 2 or len(benchmark_returns) < 2:
        return 0.0, 0.0

    excess_returns = strategy_returns - benchmark_returns
   
    daily_te = excess_returns.std(ddof=1)
    annual_te = float((daily_te * np.sqrt(252)).astype(float))

    if annual_te == 0 or np.isnan(annual_te):
        return 0.0, 0.0

    mean_excess_annual = float(excess_returns.mean() * 252)
    information_ratio = float(mean_excess_annual / annual_te)

    return annual_te, information_ratio