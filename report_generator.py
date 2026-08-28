import io
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_tearsheet_pdf(returns: pd.Series, summary: dict, export_df: pd.DataFrame) -> bytes:
  
  pdf_buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      pdf_buffer,
      pagesize=letter,
      leftMargin=36,
      rightMargin=36,
      topMargin=36,
      bottomMargin=36,
  )

  
  cum_wealth = np.exp(returns.cumsum()) * 100
  running_max = cum_wealth.cummax()
  drawdown = (cum_wealth - running_max) / running_max * 100

  
  fig, (ax1, ax2) = plt.subplots(
      2, 1, figsize=(8.5, 4.2), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
  )
  ax1.plot(returns.index, cum_wealth, color="#10B981", linewidth=1.4, label="Strategy NAV (Base 100)")
  ax1.set_title("Strategy Cumulative Wealth & Underwater Drawdown", fontsize=11, fontweight="bold", pad=8, color="#1E293B")
  ax1.set_ylabel("NAV (Base 100)", fontsize=9, color="#475569")
  ax1.grid(True, linestyle="--", alpha=0.35)
  ax1.legend(loc="upper left", fontsize=8)
  ax1.tick_params(labelsize=8)

  ax2.plot(returns.index, drawdown, color="#EF4444", linewidth=1.1, label="Drawdown %")
  ax2.fill_between(returns.index, drawdown, 0, color="#EF4444", alpha=0.25)
  ax2.set_ylabel("Drawdown (%)", fontsize=9, color="#475569")
  ax2.set_xlabel("Date", fontsize=9, color="#475569")
  ax2.grid(True, linestyle="--", alpha=0.35)
  ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
  ax2.tick_params(labelsize=8)

  plt.tight_layout()
  chart1_buf = io.BytesIO()
  plt.savefig(chart1_buf, format="png", dpi=200)
  plt.close()
  chart1_buf.seek(0)

 
  fig2, ax = plt.subplots(figsize=(8.5, 2.2))
  ret_pct = returns * 100
  ax.hist(ret_pct, bins=35, color="#3B82F6", alpha=0.7, edgecolor="white", density=True)
  ax.axvline(ret_pct.mean(), color="#10B981", linestyle="--", linewidth=1.4, label=f"Mean ({ret_pct.mean():.3f}%)")
  var_95 = np.percentile(ret_pct, 5)
  ax.axvline(var_95, color="#EF4444", linestyle=":", linewidth=1.4, label=f"95% VaR ({var_95:.3f}%)")
  ax.set_title("Daily Return Distribution & Tail Risk", fontsize=10, fontweight="bold", pad=6, color="#1E293B")
  ax.set_xlabel("Daily Log Return (%)", fontsize=8, color="#475569")
  ax.set_ylabel("Density", fontsize=8, color="#475569")
  ax.grid(True, linestyle="--", alpha=0.35)
  ax.legend(loc="upper right", fontsize=8)
  ax.tick_params(labelsize=8)

  plt.tight_layout()
  chart2_buf = io.BytesIO()
  plt.savefig(chart2_buf, format="png", dpi=200)
  plt.close()
  chart2_buf.seek(0)

 
  styles = getSampleStyleSheet()
  header_style = ParagraphStyle("DocHeader", parent=styles["Heading1"], fontSize=15, leading=18, textColor=colors.HexColor("#0F172A"), spaceAfter=2)
  sub_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#64748B"), spaceAfter=8)
  sec_style = ParagraphStyle("SecHeader", parent=styles["Heading2"], fontSize=10, leading=13, textColor=colors.HexColor("#1E293B"), spaceBefore=6, spaceAfter=4)
  cell_style = ParagraphStyle("CellText", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#1E293B"))
  cell_header = ParagraphStyle("CellHeader", parent=styles["Normal"], fontSize=8, leading=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#0F172A"))

  story = [
      Paragraph("Quantitative Strategy Performance Tearsheet", header_style),
      Paragraph(f"Period: <b>{returns.index[0].strftime('%Y-%m-%d')} to {returns.index[-1].strftime('%Y-%m-%d')}</b> &nbsp;|&nbsp; Observations: <b>{len(returns)} trading periods</b>", sub_style),
      RLImage(chart1_buf, width=7.2 * 72, height=3.0 * 72),
      Spacer(1, 3),
      RLImage(chart2_buf, width=7.2 * 72, height=1.6 * 72),
      Spacer(1, 4),
      Paragraph("Key Performance & Risk Metrics", sec_style),
  ]

  table_data = [[Paragraph("Category", cell_header), Paragraph("Metric", cell_header), Paragraph("Value", cell_header)]]
  for _, row in export_df.iterrows():
    table_data.append([
        Paragraph(str(row["Category"]), cell_style),
        Paragraph(str(row["Metric"]), cell_style),
        Paragraph(f"<b>{str(row['Value'])}</b>", cell_style),
    ])

  t = Table(table_data, colWidths=[1.6 * 72, 3.8 * 72, 1.8 * 72])
  t.setStyle(TableStyle([
      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
      ("ALIGN", (0, 0), (-1, -1), "LEFT"),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
      ("TOPPADDING", (0, 0), (-1, -1), 2.5),
      ("LINEBELOW", (0, 0), (-1, 0), 1.0, colors.HexColor("#CBD5E1")),
      ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
  ]))

  story.append(t)
  doc.build(story)
  pdf_buffer.seek(0)
  return pdf_buffer.getvalue()