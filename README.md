# 📊 Quant Tearsheet

A **Streamlit-powered** quantitative strategy tearsheet that transforms raw NAV/price time series into a professional-grade performance dashboard — complete with risk analytics, benchmark comparison, interactive visualizations, and exportable PDF report generation.

---

## 🚀 Features

| Category | What You Get |
|---|---|
| **Data Ingestion** | Paste raw CSV directly or upload a `.csv` file with automatic deduplication & daily resampling handling |
| **Return Engine** | Log-return calculation from daily NAV/price series ($\ln(P_t) - \ln(P_{t-1})$) |
| **KPI Dashboard** | Cumulative Return, CAGR, Sharpe Ratio, Sortino Ratio, Max Drawdown, Calmar Ratio |
| **Multi-Asset Benchmarks** | Live benchmark comparison against **Nifty 50**, **Sensex**, **Bitcoin**, **Ethereum**, or **Nasdaq Crypto Index** via Yahoo Finance with 6h caching |
| **Relative Metrics** | Beta, Jensen's Alpha, Tracking Error, Information Ratio |
| **Risk & Tail Risk** | Annualized Volatility, Downside Volatility (MAR = 0), Historical Daily VaR (95%), Daily CVaR / Expected Shortfall (95%) |
| **Interactive Charts** | Plotly charts with range sliders, time-selectors (1m, 3m, 6m, YTD, 1y, All), panning/zooming, and dark mode |
| **📄 PDF Tearsheet Export** | One-click export to a styled PDF performance report containing embedded vector charts and metric tables |

---

## 📊 Dashboard Preview

Once launched, the dashboard provides:

1. **Header & Date Range Summary** — Auto-detects analysis period and total strategy trading days.
2. **Top KPI Row** — Instant view of strategy performance & benchmark sensitivity (Beta/Alpha).
3. **Tabbed Interactive Visualizations**:
   - 📈 **Cumulative Wealth Growth** (Base 100 strategy vs benchmark overlay with time rangesliders)
   - 📉 **Underwater Drawdown Curve** (Area-shaded historical drawdown depth)
   - 📊 **Returns & Tail Risk** (Histogram of daily returns with 95% Historical VaR line)
4. **Detailed Risk & Relative Summary Table** — Metrics breakdown with plain-English financial interpretations.
5. **📥 PDF Report Generator** — Generate and download `Quantitative_Strategy_Tearsheet.pdf` on demand.

---

## 💻 Getting Started

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

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
Quant-Tearsheet/
├── app.py              # Main Streamlit application, dashboard layout & export trigger
├── data_loader.py      # Data pipeline: CSV parsing, log-return calculation & cached yfinance fetcher
├── metrics.py          # Quantitative metric calculations (Returns, Risk, Tail Risk, Beta, Alpha, Tracking Error, IR)
├── report_generator.py # PDF report builder using ReportLab and Matplotlib
├── visuals.py          # Plotly interactive chart builders (Wealth Growth, Drawdown, Distribution)
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md           # Project documentation
```

---

## 📑 Input Data Format

The application accepts a **two-column CSV** (with or without header row):

| Column 0 | Column 1 |
|---|---|
| Date (any standard date format) | Price / NAV |

**Example:**

```csv
Date,NAV
2024-01-01,100000.00
2024-01-02,101250.00
2024-01-03,102100.50
```

---

## 📐 Metrics Reference

| Metric | Description & Formula |
|---|---|
| **Cumulative Return** | Total return over entire period: $\exp(\sum r_t) - 1$ |
| **CAGR** | Compound Annual Growth Rate: $\exp(\bar{r} \times 252) - 1$ |
| **Annual Volatility** | Annualized standard deviation of daily log returns: $\sigma_{daily} \times \sqrt{252}$ |
| **Downside Volatility** | Annualized downside deviation considering negative returns below MAR = 0 |
| **Sharpe Ratio** | Risk-adjusted return: $\text{CAGR} / \text{Annual Volatility}$ |
| **Sortino Ratio** | Downside risk-adjusted return: $\text{CAGR} / \text{Downside Volatility}$ |
| **Max Drawdown** | Deepest peak-to-trough drop in cumulative wealth |
| **Calmar Ratio** | Drawdown-adjusted return: $\text{CAGR} / \|\text{Max Drawdown}\|$ |
| **Daily VaR (95%)** | Historical Value at Risk: 5th percentile of daily returns |
| **Daily CVaR (95%)** | Expected Shortfall: mean loss on days breaching 95% VaR threshold |
| **Beta** | Sensitivity to benchmark: $\text{Cov}(R_s, R_b) / \text{Var}(R_b)$ |
| **Jensen's Alpha** | Annualized excess return over market sensitivity: $\text{CAGR}_s - \beta \times \text{CAGR}_b$ |
| **Tracking Error** | Annualized standard deviation of active excess returns: $\sigma(R_s - R_b) \times \sqrt{252}$ |
| **Information Ratio** | Active return per unit of active risk: $\text{Mean}(R_s - R_b) \times 252 / \text{Tracking Error}$ |

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web application UI
- **[Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)** — Financial data processing & mathematical calculations
- **[Plotly](https://plotly.com/python/)** — Interactive financial charts & time controls
- **[yfinance](https://github.com/ranaroussi/yfinance)** — Historical market benchmark data API
- **[ReportLab](https://www.reportlab.com/) & [Matplotlib](https://matplotlib.org/)** — Automated PDF tearsheet document generation

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).
