# 📊 Quant Tearsheet

A **Streamlit-powered** quantitative strategy tearsheet that transforms raw NAV/price data into a professional-grade performance dashboard — complete with risk analytics, benchmark comparison, and interactive visualizations.

---

## ✨ Features

| Category | What You Get |
|---|---|
| **Data Input** | Paste raw CSV directly or upload a `.csv` file |
| **Return Engine** | Log-return calculation from daily NAV/price series |
| **KPI Dashboard** | Cumulative Return, CAGR, Sharpe, Sortino, Max Drawdown, Calmar |
| **Benchmark Comparison** | Live comparison against **Nifty 50** or **Sensex** via Yahoo Finance |
| **Relative Metrics** | Beta, Jensen's Alpha, Tracking Error, Information Ratio |
| **Risk Analytics** | Annualized Volatility, Downside Volatility, VaR (95%), CVaR / Expected Shortfall (95%) |
| **Interactive Charts** | Cumulative Wealth Growth, Underwater Drawdown Curve, Return Distribution with VaR overlay |

---

## 🖼️ Dashboard Preview

Once launched, the app displays:

1. **Top KPI row** — key performance metrics at a glance  
2. **Tabbed visualizations** — Cumulative Wealth · Drawdown Curve · Return Distribution  
3. **Detailed risk table** — full breakdown with plain-English interpretations  

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/PravarP11/Quant-Tearsheet.git
cd Quant-Tearsheet

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
Quant-Tearsheet/
├── app.py              # Main Streamlit application & layout
├── data_loader.py      # CSV parsing, log-return pipeline & benchmark fetcher
├── metrics.py          # Performance & risk metric calculations
├── visuals.py          # Plotly chart builders (wealth, drawdown, distribution)
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

---

## 📋 Input Format

The app expects a **two-column CSV** (with or without headers):

| Column 0 | Column 1 |
|---|---|
| Date (any parseable format) | Price / NAV |

**Example:**

```csv
Date,NAV
2024-01-01,100000.00
2024-01-02,101250.00
2024-01-03,102100.50
```

---

## 🧮 Metrics Reference

| Metric | Formula / Description |
|---|---|
| **Cumulative Return** | `exp(Σ log returns) − 1` |
| **CAGR** | `exp(mean daily log return × 252) − 1` |
| **Sharpe Ratio** | `CAGR / Annualized Volatility` |
| **Sortino Ratio** | `CAGR / Downside Volatility` |
| **Max Drawdown** | Largest peak-to-trough decline in cumulative wealth |
| **Calmar Ratio** | `CAGR / |Max Drawdown|` |
| **VaR (95%)** | 5th percentile of daily returns (historical) |
| **CVaR (95%)** | Mean of returns below VaR threshold |
| **Beta** | `Cov(strategy, benchmark) / Var(benchmark)` |
| **Jensen's Alpha** | `CAGR_strategy − β × CAGR_benchmark` (annualized) |
| **Tracking Error** | `Std(excess returns) × √252` |
| **Information Ratio** | `Mean(excess returns) × 252 / Tracking Error` |

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — interactive web UI  
- **[Pandas](https://pandas.pydata.org/)** & **[NumPy](https://numpy.org/)** — data wrangling & numerics  
- **[Plotly](https://plotly.com/python/)** — interactive charting  
- **[yfinance](https://github.com/ranaroussi/yfinance)** — benchmark data from Yahoo Finance  

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
