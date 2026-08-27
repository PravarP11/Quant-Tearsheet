import numpy as np
import pandas as pd
import streamlit as st

# Custom modules
from data_loader import (
    align_strategy_and_benchmark,
    data_pipeline,
    fetch_benchmark_returns,
)
from metrics import (
    beta_and_alpha,
    generate_metrics_summary,
    tracking_error_and_ir,
)
from visuals import (
    cumulative_graph,
    return_distribution_graph,
    underwater_graph,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Quantitative Strategy Tearsheet",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar Configuration ---
with st.sidebar:
  st.header("Data Input")

  data_source = st.radio(
      "Select Data Source:",
      options=["Paste Raw CSV", "Upload CSV File"],
      index=0,
  )

  raw_csv_content = ""

  if data_source == "Paste Raw CSV":
    raw_csv_content = st.text_area(
        "Paste CSV Content Below:",
        value="",
        placeholder=(
            "Date,NAV\n2024-01-01,100000.00\n2024-01-02,101250.00\n2024-01-03,102100.50"
        ),
        height=260,
        help="Ensure Column 0 is Date and Column 1 is Price/NAV.",
    )
  else:
    uploaded_file = st.file_uploader("Upload NAV CSV File", type=["csv"])
    if uploaded_file is not None:
      raw_csv_content = uploaded_file.getvalue().decode("utf-8")

  st.markdown("---")
  st.subheader("Benchmark Index")
  enable_benchmark = st.checkbox("Compare against Benchmark", value=True)
  benchmark_choice = st.selectbox(
      "Select Index",
      options=[
          "Nifty 50",
          "Sensex",
          "Bitcoin (Crypto Market Proxy)",
          "Ethereum",
          "Nasdaq Crypto Index (Hashdex ETF)",
      ],
  )

# --- Data Validation & Ingestion ---
if not raw_csv_content.strip():
  st.info(
      "👈 Please upload a CSV file or paste raw CSV data in the sidebar to"
      " generate the tearsheet."
  )
  st.stop()

returns = None
try:
  returns = data_pipeline(raw_csv_content)
except Exception as e:
  st.error(f"Error parsing CSV input: {e}")
  st.stop()

if returns is None or returns.empty or len(returns) < 2:
  st.error(
      "Insufficient data points. Please supply at least 2 valid historical"
      " price entries."
  )
  st.stop()

# --- Main Dashboard Header & Metrics ---
if returns is not None and not returns.empty:
  st.title("📊 Quantitative Strategy Tearsheet")

  start_date = str(pd.to_datetime(returns.index[0]).date())
  end_date = str(pd.to_datetime(returns.index[-1]).date())
  st.caption(
      f"Analysis Period: **{start_date}** to **{end_date}** | Total Strategy"
      f" Trading Days: **{len(returns)}**"
  )

  # --- Fetch Benchmark & Align (if enabled) ---
  bench_returns = None
  strat_aligned = returns
  beta_val, alpha_val = 0.0, 0.0
  te_val, ir_val = 0.0, 0.0

  if enable_benchmark:
    with st.spinner(
        f"Fetching historical market data for {benchmark_choice}..."
    ):
      raw_bench = fetch_benchmark_returns(
          start_date, end_date, benchmark_choice
      )
      if not raw_bench.empty:
        strat_aligned, bench_returns = align_strategy_and_benchmark(
            returns, raw_bench
        )
        beta_val, alpha_val = beta_and_alpha(strat_aligned, bench_returns)
        te_val, ir_val = tracking_error_and_ir(strat_aligned, bench_returns)
      else:
        st.warning(
            f"⚠️ Could not retrieve market data for **{benchmark_choice}** over"
            " the selected date range. Displaying strategy alone."
        )

  st.markdown("---")

  # --- Unified Strategy Metrics Generation ---
  summary = generate_metrics_summary(strat_aligned)

  # --- Top Row: Key Performance Indicators ---
  if enable_benchmark and bench_returns is not None:
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8 = st.columns(8)
    kpi1.metric(
        label="Cumulative Return",
        value=f"{summary['Cumulative Return'] * 100:.2f}%",
    )
    kpi2.metric(label="CAGR", value=f"{summary['CAGR'] * 100:.2f}%")
    kpi3.metric(label="Sharpe", value=f"{summary['Sharpe Ratio']:.2f}")
    kpi4.metric(label="Sortino", value=f"{summary['Sortino Ratio']:.2f}")
    kpi5.metric(
        label="Max DD", value=f"{summary['Max Drawdown'] * 100:.2f}%"
    )
    kpi6.metric(label="Calmar", value=f"{summary['Calmar Ratio']:.2f}")
    kpi7.metric(label=f"Beta ({benchmark_choice})", value=f"{beta_val:.2f}")
    kpi8.metric(label="Alpha (Annual)", value=f"{alpha_val * 100:.2f}%")
  else:
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric(
        label="Cumulative Return",
        value=f"{summary['Cumulative Return'] * 100:.2f}%",
    )
    kpi2.metric(label="CAGR", value=f"{summary['CAGR'] * 100:.2f}%")
    kpi3.metric(label="Sharpe Ratio", value=f"{summary['Sharpe Ratio']:.2f}")
    kpi4.metric(label="Sortino Ratio", value=f"{summary['Sortino Ratio']:.2f}")
    kpi5.metric(
        label="Max Drawdown", value=f"{summary['Max Drawdown'] * 100:.2f}%"
    )
    kpi6.metric(label="Calmar Ratio", value=f"{summary['Calmar Ratio']:.2f}")

  st.markdown("---")

  # --- Middle Section: Visualizations ---
  tab1, tab2, tab3 = st.tabs(
      ["📈 Cumulative Wealth", "📉 Drawdown Curve", "📊 Returns & Tail Risk"]
  )

  with tab1:
    fig_wealth = cumulative_graph(
        strategy_returns=strat_aligned,
        benchmark_returns=bench_returns,
        benchmark_name=benchmark_choice if enable_benchmark else "Benchmark",
    )
    st.plotly_chart(
        fig_wealth,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "doubleClick": "reset+autosize",
            "modeBarButtonsToAdd": ["drawline", "eraseshape"],
        },
    )

  with tab2:
    fig_drawdown = underwater_graph(strat_aligned)
    st.plotly_chart(
        fig_drawdown,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "doubleClick": "reset+autosize",
            "modeBarButtonsToAdd": ["drawline", "eraseshape"],
        },
    )

  with tab3:
    fig_dist = return_distribution_graph(strat_aligned)
    st.plotly_chart(fig_dist, use_container_width=True)

  # --- Bottom Section: Risk & Volatility Breakdown ---
  st.subheader("📑 Detailed Risk & Relative Performance Summary")

  table_rows = [
      (
          "Annualized Volatility",
          f"{summary['Annual Volatility'] * 100:.2f}%",
          "Overall standard deviation scaled to 252 trading days",
      ),
      (
          "Downside Volatility",
          f"{summary['Downside Volatility'] * 100:.2f}%",
          (
              "Annualized dispersion considering only negative return days (MAR"
              " = 0)"
          ),
      ),
      (
          "Historical Daily VaR (95%)",
          f"{summary['Daily VaR (95%)'] * 100:.2f}%",
          "Maximum expected daily loss on 95% of trading days",
      ),
      (
          "Historical Daily CVaR / Expected Shortfall (95%)",
          f"{summary['Daily CVaR (95%)'] * 100:.2f}%",
          "Average loss magnitude incurred on days breaching the VaR threshold",
      ),
  ]

  if enable_benchmark and bench_returns is not None:
    table_rows.extend([
        (
            f"Beta (vs {benchmark_choice})",
            f"{beta_val:.2f}",
            (
                "Sensitivity of strategy returns relative to benchmark index"
                " movements"
            ),
        ),
        (
            f"Jensen's Alpha (vs {benchmark_choice})",
            f"{alpha_val * 100:.2f}%",
            (
                "Annualized excess return generated over benchmark-implied"
                " return"
            ),
        ),
        (
            f"Tracking Error (vs {benchmark_choice})",
            f"{te_val * 100:.2f}%",
            "Annualized standard deviation of daily excess returns",
        ),
        (
            f"Information Ratio (vs {benchmark_choice})",
            f"{ir_val:.2f}",
            (
                "Mean active excess return generated per unit of active risk"
                " (Tracking Error)"
            ),
        ),
    ])

  df_metrics = pd.DataFrame(
      table_rows, columns=["Metric Name", "Value", "Interpretation"]
  )
  st.dataframe(df_metrics, use_container_width=True, hide_index=True)