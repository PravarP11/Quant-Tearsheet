import numpy as np
import pandas as pd
import plotly.graph_objects as go
from metrics import drawdown_series,historical_var

def cumulative_graph(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series = None,
    benchmark_name: str = "Benchmark",
) -> go.Figure:
  #Plots cumulative wealth growth (Base 100) with marker dots at each data point.
  strategy_wealth = np.exp(strategy_returns.cumsum()) * 100

  fig = go.Figure()

  fig.add_trace(
      go.Scatter(
          x=strategy_wealth.index,
          y=strategy_wealth.values,
          mode="lines",
          name="Strategy",
          line=dict(color="#00D084", width=2),
          #marker=dict(size=8, color="#00D084"),
          hovertemplate="<b>Strategy</b>: %{y:.2f}<extra></extra>",
      )
  )

  # Benchmark Trajectory 
  if benchmark_returns is not None and not benchmark_returns.empty:
    bench_wealth = np.exp(benchmark_returns.cumsum()) * 100
    fig.add_trace(
        go.Scatter(
            x=bench_wealth.index,
            y=bench_wealth.values,
            mode="lines",
            name=benchmark_name,
            line=dict(color="#3399FF", width=1.5, dash="dot"),
            #marker=dict(size=8, color="#3399FF"),
            hovertemplate=f"<b>{benchmark_name}</b>: %{{y:.2f}}<extra></extra>",
        )
    )

  fig.update_layout(
     title="Cumulative Wealth Growth (Base 100)",
      xaxis_title="Date",
      yaxis_title="Portfolio Value",
      template="plotly_dark",
      hovermode="x unified",
      dragmode="pan",  # Click and drag to pan
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(
          l=70, r=40, t=80, b=40
      ),  # Padding on left to easily hover on price axis
      xaxis=dict(
          fixedrange=False,  # Unlocks X-axis for time scrolling & dragging
          type="date",
          rangeslider=dict(
              visible=True,
              thickness=0.08,
              bgcolor="rgba(255, 255, 255, 0.05)",
          ),
          rangeselector=dict(
              buttons=list([
                  dict(
                      count=1, label="1m", step="month", stepmode="backward"
                  ),
                  dict(
                      count=3, label="3m", step="month", stepmode="backward"
                  ),
                  dict(
                      count=6, label="6m", step="month", stepmode="backward"
                  ),
                  dict(count=1, label="YTD", step="year", stepmode="todate"),
                  dict(count=1, label="1y", step="year", stepmode="backward"),
                  dict(step="all", label="All"),
              ]),
              bgcolor="#1E222D",
              activecolor="#2962FF",
              font=dict(color="#D1D4DC"),
          ),
      ),
      yaxis=dict(
          fixedrange=False,  # Unlocks Y-axis for vertical price scrolling & stretching
          autorange=True,
          side="left",
          ticks="outside",
          showgrid=True,
          zeroline=False,
      ),
  )
  return fig



def underwater_graph( log_returns: pd.Series) -> go.Figure:
    #Plots the Drawdown curve with a shaded area fill and markers

    if log_returns.empty:
        return go.Figure()
    dd_series = drawdown_series(log_returns)

    drawdown_pct = dd_series*100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=drawdown_pct.index,
            y=drawdown_pct.values,
            mode="lines",
            name="Drawdown (%)",
            line=dict(color="#FF4B4B", width=1.5),
            #marker=dict(
            #   size=8,
            #    color="#FF4B4B",
            #   symbol="circle"
            #),
            fill="tozeroy",                        
            fillcolor="rgba(255, 75, 75, 0.25)",   
            hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Drawdown</b>: %{y:.2f}%<extra></extra>"
        )
    )

    fig.update_layout(
      title="Historical Underwater Chart (Drawdowns)",
      xaxis_title="Date",
      yaxis_title="Drawdown (%)",
      template="plotly_dark",
      hovermode="x unified",
      dragmode="pan",
      margin=dict(l=70, r=40, t=80, b=40),
      xaxis=dict(
          fixedrange=False,
          type="date",
          rangeslider=dict(
              visible=True,
              thickness=0.08,
              bgcolor="rgba(255, 255, 255, 0.05)",
          ),
          rangeselector=dict(
              buttons=list([
                  dict(
                      count=1, label="1m", step="month", stepmode="backward"
                  ),
                  dict(
                      count=3, label="3m", step="month", stepmode="backward"
                  ),
                  dict(
                      count=6, label="6m", step="month", stepmode="backward"
                  ),
                  dict(count=1, label="YTD", step="year", stepmode="todate"),
                  dict(count=1, label="1y", step="year", stepmode="backward"),
                  dict(step="all", label="All"),
              ]),
              bgcolor="#1E222D",
              activecolor="#2962FF",
              font=dict(color="#D1D4DC"),
          ),
      ),
      yaxis=dict(
          fixedrange=False,  # Unlocks Y-axis for drawdown percentage vertical scaling
          autorange=True,
          side="left",
          ticks="outside",
          showgrid=True,
          zeroline=True,
          zerolinecolor="#444",
      ),
    )

    return fig


def return_distribution_graph(log_returns: pd.Series) -> go.Figure:
    #Plots daily return distribution histogram with 95% Historical VaR line.

    if log_returns.empty:
        return go.Figure()

    simple_returns_pct = (np.exp(log_returns)-1)*100

    var_loss_ratio = historical_var(log_returns, 0.95)

    var_x_coord = -var_loss_ratio*100

    fig = go.Figure()

  
    fig.add_trace(
      go.Histogram(
          x=simple_returns_pct,
          nbinsx=20,
          name="Daily Returns",
          marker_color="#3399FF",  
          opacity=0.75,
          hovertemplate=(
              "<b>Return Bin</b>: %{x:.2f}%<br><b>Days Count</b>:"
              " %{y}<extra></extra>"
            ),
        )
    )

    fig.add_vline(
      x=var_x_coord,
      line_dash="dash",
      line_color="#FFAA00", 
      line_width=2,
      annotation_text=f"VaR (95%): {var_loss_ratio * 100:.2f}%",
      annotation_position="top left",
      annotation_font=dict(color="#FFAA00"),
    )

    fig.update_layout(
      title="Daily Returns Distribution & Tail Risk",
      xaxis_title="Daily Return (%)",
      yaxis_title="Frequency (Number of Days)",
      template="plotly_dark",
      bargap=0.05,
      margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig
