"""
╔══════════════════════════════════════════════════════════╗
║   SILVER INTELLIGENCE DASHBOARD  —  MCX Pro Edition     ║
║   CXO Analytics Suite | Live Market Data | April 2026   ║
╚══════════════════════════════════════════════════════════╝
Tabs: Overview | COMEX→MCX | Macro Framework |
      Fundamentals | Gold-Silver Ratio | Technical Analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import io
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Silver Intelligence | MCX Pro",
    page_icon="🥈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
# DESIGN TOKENS  — IBM Plex Mono + Syne display font
# ═══════════════════════════════════════════════════════════
BG_MAIN     = "#080c14"
BG_CARD     = "#0d1220"
BG_SURFACE  = "#111826"
BG_ELEVATED = "#161f30"

SIL         = "#d0d8e8"   # silver
SIL_GLOW    = "#c8d4f0"
GOLD_C      = "#e8c050"
BULL        = "#22d18a"
BEAR        = "#f04060"
WARN        = "#f0a030"
ACCENT      = "#4080ff"
MUTED       = "#5a6a82"
GRID        = "#1a2438"
TEXT        = "#c8d4e8"

CHART_BASE = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_MAIN,
    font=dict(color=TEXT, family="IBM Plex Mono, monospace", size=11),
    margin=dict(l=50, r=20, t=44, b=36),
    xaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False, linecolor=GRID,
                tickfont=dict(color=MUTED, size=10)),
    yaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False, linecolor=GRID,
                tickfont=dict(color=MUTED, size=10)),
    hovermode="x unified",
    hoverlabel=dict(bgcolor=BG_ELEVATED, bordercolor=GRID,
                    font=dict(color=TEXT, family="IBM Plex Mono", size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID,
                font=dict(size=10, color=MUTED)),
)

# ═══════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Syne:wght@600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

.stApp {{ background:{BG_MAIN}; color:{TEXT}; font-family:'IBM Plex Mono', monospace; }}

/* scrollbar */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:{BG_MAIN}; }}
::-webkit-scrollbar-thumb {{ background:{GRID}; border-radius:3px; }}

/* header strip */
.dash-header {{
  background:linear-gradient(90deg,{BG_CARD} 0%,{BG_SURFACE} 100%);
  border-bottom:1px solid {GRID};
  padding:1.25rem 2rem;
  margin:-1rem -1rem 1.5rem;
}}
.dash-title {{
  font-family:'Syne',sans-serif;
  font-size:1.55rem;
  font-weight:800;
  color:{SIL_GLOW};
  letter-spacing:0.01em;
  margin:0;
}}
.dash-sub {{
  font-size:0.72rem;
  color:{MUTED};
  letter-spacing:0.08em;
  text-transform:uppercase;
  margin:0.2rem 0 0;
}}

/* KPI card */
.kpi {{
  background:{BG_CARD};
  border:1px solid {GRID};
  border-radius:10px;
  padding:1rem 1.1rem;
  position:relative;
  overflow:hidden;
}}
.kpi::before {{
  content:'';
  position:absolute;
  top:0; left:0;
  width:3px; height:100%;
}}
.kpi.bull::before {{ background:{BULL}; }}
.kpi.bear::before {{ background:{BEAR}; }}
.kpi.warn::before {{ background:{WARN}; }}
.kpi.neu::before  {{ background:{MUTED}; }}
.kpi .lbl {{
  font-size:0.68rem;
  color:{MUTED};
  text-transform:uppercase;
  letter-spacing:0.10em;
  margin-bottom:0.4rem;
}}
.kpi .val {{
  font-family:'Syne',sans-serif;
  font-size:1.45rem;
  font-weight:700;
  line-height:1.1;
}}
.kpi .sub {{
  font-size:0.72rem;
  margin-top:0.25rem;
  color:{MUTED};
}}
.kpi .chg.up   {{ color:{BULL}; }}
.kpi .chg.down {{ color:{BEAR}; }}
.kpi .chg.flat {{ color:{MUTED}; }}

/* signal pill */
.pill {{
  display:inline-block;
  font-size:0.65rem;
  font-weight:600;
  letter-spacing:0.08em;
  padding:0.2rem 0.55rem;
  border-radius:20px;
  text-transform:uppercase;
  border:1px solid;
}}
.pill.bull {{ color:{BULL}; border-color:{BULL}33; background:{BULL}18; }}
.pill.bear {{ color:{BEAR}; border-color:{BEAR}33; background:{BEAR}18; }}
.pill.warn {{ color:{WARN}; border-color:{WARN}33; background:{WARN}18; }}
.pill.neu  {{ color:{MUTED}; border-color:{MUTED}33; background:{MUTED}18; }}

/* info / insight blocks */
.insight {{
  background:{BG_SURFACE};
  border-left:3px solid {ACCENT};
  border-radius:0 8px 8px 0;
  padding:.75rem 1rem;
  margin:.6rem 0;
  font-size:.8rem;
  color:{TEXT};
  line-height:1.6;
}}
.warn-box {{
  background:rgba(240,160,48,.07);
  border-left:3px solid {WARN};
  border-radius:0 8px 8px 0;
  padding:.75rem 1rem;
  margin:.6rem 0;
  font-size:.8rem;
  color:{WARN};
}}

/* signal row */
.sig-row {{
  display:flex;
  align-items:center;
  justify-content:space-between;
  background:{BG_SURFACE};
  border:1px solid {GRID};
  border-radius:7px;
  padding:.5rem .8rem;
  margin:.3rem 0;
  font-size:.8rem;
}}
.sig-row .name {{ color:{MUTED}; }}

/* section heading */
.sec {{
  font-family:'Syne',sans-serif;
  font-size:.85rem;
  font-weight:700;
  color:{MUTED};
  text-transform:uppercase;
  letter-spacing:.10em;
  padding-bottom:.4rem;
  border-bottom:1px solid {GRID};
  margin-bottom:.75rem;
}}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{
  background:{BG_CARD};
  border-radius:10px;
  padding:.3rem;
  gap:.25rem;
  border:1px solid {GRID};
}}
.stTabs [data-baseweb="tab"] {{
  background:transparent;
  border-radius:7px;
  color:{MUTED};
  font-family:'IBM Plex Mono',monospace;
  font-size:.78rem;
  letter-spacing:.04em;
  padding:.45rem .9rem;
}}
.stTabs [aria-selected="true"] {{
  background:{BG_ELEVATED} !important;
  color:{SIL_GLOW} !important;
}}

/* data table */
.stDataFrame {{ border-radius:10px; overflow:hidden; }}

/* hide streamlit chrome */
#MainMenu,footer,header {{ visibility:hidden; }}
.block-container {{ padding-top:1rem; max-width:100%; }}

/* slider */
.stSlider [data-baseweb="slider"] {{ padding:0; }}

div[data-testid="metric-container"] {{
  background:{BG_CARD};
  border:1px solid {GRID};
  border-radius:8px;
  padding:.5rem .75rem;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# DATA LAYER  — fetch with 5-min cache
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def _yf(ticker, period="2y", interval="1d"):
    try:
        # User-Agent header helps bypass bot blockers on cloud servers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        df = yf.Ticker(ticker, session=session).history(period=period, interval=interval, auto_adjust=True)
        df.index = df.index.tz_localize(None)
        return df.dropna(subset=["Close"])
    except Exception as e:
        print(f"Error fetching Yahoo Finance data for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def _fred(series_id):
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Adding timeout explicitly to requests to prevent permanent hanging
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        
        df = pd.read_csv(io.StringIO(response.text), parse_dates=["DATE"], index_col="DATE")
        df.columns = ["value"]
        df = df[df["value"] != "."].copy()
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        return df.loc[df.index >= df.index[-1] - pd.DateOffset(years=2)]
    except Exception as e:
        print(f"Error fetching FRED data for {series_id}: {e}")
        return pd.DataFrame()


def _last(df, col="Close"):
    try:
        return float(df[col].dropna().iloc[-1])
    except Exception:
        return np.nan


def _pct(df, col="Close", n=1):
    try:
        s = df[col].dropna()
        return float((s.iloc[-1] - s.iloc[-n]) / s.iloc[-n] * 100)
    except Exception:
        return np.nan


# ─── technical helpers ───────────────────────────────────

def calc_rsi(s: pd.Series, n=14) -> pd.Series:
    d = s.diff()
    g = d.clip(lower=0).ewm(com=n - 1, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(com=n - 1, adjust=False).mean()
    return 100 - (100 / (1 + g / l.replace(0.0, np.nan)))


def calc_bb(s: pd.Series, n=20, k=2):
    m = s.rolling(n).mean()
    sd = s.rolling(n).std()
    return m + k * sd, m, m - k * sd


def calc_obv(s: pd.Series, v: pd.Series) -> pd.Series:
    sign = np.sign(s.diff().fillna(0))
    return (v * sign).cumsum()


def mcx_est(comex_oz, usdinr, duty=0.10):
    """COMEX $/oz → MCX ₹/kg"""
    return comex_oz * 32.1507 * usdinr * (1 + duty)


# ═══════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════

with st.spinner("⚡ Connecting to live feeds…"):
    ag     = _yf("SI=F",      "2y")   # COMEX silver
    au     = _yf("GC=F",      "2y")   # COMEX gold
    dxy    = _yf("DX-Y.NYB",  "2y")   # Dollar Index
    inr    = _yf("USDINR=X",  "2y")   # USD/INR
    slv    = _yf("SLV",       "1y")   # SLV ETF
    pall   = _yf("PA=F",      "1y")   # Palladium (industrial ref)
    copper = _yf("HG=F",      "1y")   # Copper (China industrial proxy)

    tips    = _fred("DFII10")   # 10yr Real yield
    dgs10   = _fred("DGS10")    # 10yr Nominal
    t10yie  = _fred("T10YIE")   # 10yr Breakeven inflation

# ─── derived values ──────────────────────────────────────

ag_px    = _last(ag)
au_px    = _last(au)
dxy_px   = _last(dxy)
inr_px   = _last(inr)
slv_px   = _last(slv)
cu_px    = _last(copper)

ag_d1    = _pct(ag,  n=1)
ag_d5    = _pct(ag,  n=5)
ag_d20   = _pct(ag,  n=20)
au_d1    = _pct(au,  n=1)
dxy_d1   = _pct(dxy, n=1)
inr_d1   = _pct(inr, n=1)

mcx_px   = mcx_est(ag_px, inr_px) if not (np.isnan(ag_px) or np.isnan(inr_px)) else np.nan
mcx_d1   = ag_d1 + inr_d1 if not (np.isnan(ag_d1) or np.isnan(inr_d1)) else np.nan

gsr_now  = au_px / ag_px if not (np.isnan(ag_px) or np.isnan(au_px)) else np.nan
ry_now   = float(tips["value"].iloc[-1]) if not tips.empty else np.nan

dxy_200  = float(dxy["Close"].rolling(200).mean().dropna().iloc[-1]) if len(dxy) >= 200 else np.nan
dxy_above_200 = (not np.isnan(dxy_px)) and (not np.isnan(dxy_200)) and (dxy_px > dxy_200)

ag_200   = float(ag["Close"].rolling(200).mean().dropna().iloc[-1]) if len(ag) >= 200 else np.nan
ag_above_200 = (not np.isnan(ag_px)) and (not np.isnan(ag_200)) and (ag_px > ag_200)

# ─── macro signal computation ────────────────────────────

def macro_signal(dxy_p, dxy_2, ry_n, tips_df, inr_d, ag_d):
    score = 0
    rows  = []

    if not np.isnan(dxy_p) and not np.isnan(dxy_2):
        s = -1 if dxy_p > dxy_2 else 1
        rows.append(("DXY vs 200-DMA", s, f"{dxy_p:.1f} {'above' if dxy_p>dxy_2 else 'below'} 200-DMA {dxy_2:.1f}"))
    else:
        rows.append(("DXY vs 200-DMA", 0, "data unavailable"))
    score += rows[-1][1]

    if not np.isnan(ry_n):
        s = 1 if ry_n < 0 else (0 if ry_n < 1 else -1)
        rows.append(("10yr Real Yield", s, f"{ry_n:+.2f}%"))
    else:
        rows.append(("10yr Real Yield", 0, "data unavailable"))
    score += rows[-1][1]

    if len(tips_df) >= 30:
        chg = float(tips_df["value"].iloc[-1] - tips_df["value"].iloc[-30])
        s = 1 if chg < -0.15 else (-1 if chg > 0.15 else 0)
        rows.append(("Real Yield 30d Δ", s, f"30d change: {chg:+.2f}%"))
    else:
        rows.append(("Real Yield 30d Δ", 0, "data unavailable"))
    score += rows[-1][1]

    if not np.isnan(inr_d):
        s = -1 if inr_d > 0.5 else (1 if inr_d < -0.5 else 0)
        rows.append(("USD/INR 1d Δ", s, f"{inr_d:+.2f}% (INR depreciation = MCX cost ↑)"))
    else:
        rows.append(("USD/INR 1d Δ", 0, "data unavailable"))
    score += rows[-1][1]

    if not np.isnan(ag_d):
        s = 1 if ag_d > 0 else (-1 if ag_d < 0 else 0)
        rows.append(("Silver 20d Momentum", s, f"{ag_d:+.2f}%"))
    else:
        rows.append(("Silver 20d Momentum", 0, "data unavailable"))
    score += rows[-1][1]

    return score, rows

macro_score, macro_rows = macro_signal(dxy_px, dxy_200, ry_now, tips, inr_d1, ag_d20)

overall_macro = (
    "STRONGLY BULLISH" if macro_score >= 4  else
    "BULLISH"          if macro_score >= 2  else
    "NEUTRAL"          if macro_score == 0  else
    "BEARISH"          if macro_score >= -2 else
    "STRONGLY BEARISH"
)
macro_col = BULL if macro_score > 0 else (BEAR if macro_score < 0 else WARN)

# ─── GSR signal ──────────────────────────────────────────

def gsr_interpret(g):
    if np.isnan(g):
        return "N/A", MUTED, "—", "neu"
    if g > 80:
        return "Silver Deeply Undervalued", BULL, "Favour SILVER — Full risk allocation", "bull"
    if g > 60:
        return "Silver Mildly Undervalued", BULL, "Lean SILVER — Standard allocation", "bull"
    if g > 45:
        return "Near Historical Mean", WARN, "Neutral — technicals drive selection", "warn"
    if g > 35:
        return "Silver Moderately Expensive", BEAR, "Lean GOLD — Reduce silver 50%", "bear"
    return "Silver Extremely Expensive", BEAR, "Avoid Silver — Switch to GOLD", "bear"


gsr_label, gsr_col, gsr_action, gsr_pill_cls = gsr_interpret(gsr_now)

# ─── RSI + BB ────────────────────────────────────────────

rsi_series = calc_rsi(ag["Close"]) if not ag.empty else pd.Series(dtype=float)
rsi_now    = float(rsi_series.dropna().iloc[-1]) if not rsi_series.empty else np.nan

bb_up, bb_mid, bb_lo = (calc_bb(ag["Close"]) if not ag.empty
                          else (pd.Series(), pd.Series(), pd.Series()))
bb_pos = float((ag["Close"].iloc[-1] - bb_lo.iloc[-1]) /
               (bb_up.iloc[-1] - bb_lo.iloc[-1]) * 100) if not ag.empty else np.nan

bb_width     = ((bb_up - bb_lo) / bb_mid * 100) if not ag.empty else pd.Series(dtype=float)
bb_w_now     = float(bb_width.dropna().tail(5).mean()) if not bb_width.empty else np.nan
bb_w_avg     = float(bb_width.dropna().tail(60).mean()) if not bb_width.empty else np.nan
squeeze      = (not np.isnan(bb_w_now)) and (not np.isnan(bb_w_avg)) and (bb_w_now < bb_w_avg * 0.70)

obv_series   = calc_obv(ag["Close"], ag["Volume"]) if not ag.empty else pd.Series(dtype=float)
obv_rising   = (not obv_series.empty) and float(obv_series.iloc[-1]) > float(obv_series.iloc[-20]) if len(obv_series) >= 20 else None

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════

now_str = datetime.now().strftime("%d %b %Y · %H:%M IST")
st.markdown(f"""
<div class="dash-header">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
    <div>
      <p class="dash-title">🥈 Silver Intelligence Dashboard</p>
      <p class="dash-sub">MCX Pro · CXO Executive Analytics · Live Market Data</p>
    </div>
    <div style="text-align:right;">
      <div style="font-size:.68rem;color:{MUTED};text-transform:uppercase;letter-spacing:.08em;">Live as of</div>
      <div style="font-family:'Syne',sans-serif;font-size:.95rem;color:{SIL_GLOW};font-weight:700;">{now_str}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# KPI STRIP  — 6 cards
# ═══════════════════════════════════════════════════════════

def chg_html(val):
    if np.isnan(val):
        return '<span class="chg flat">—</span>'
    cls = "up" if val > 0 else "down"
    arr = "▲" if val > 0 else "▼"
    return f'<span class="chg {cls}">{arr} {abs(val):.2f}%</span>'

def pill(label, cls):
    return f'<span class="pill {cls}">{label}</span>'

# Safe formatting for when API feeds fail and return NaN
ag_px_str  = f"${ag_px:,.2f}" if not np.isnan(ag_px) else "N/A"
mcx_px_str = f"₹{mcx_px:,.0f}" if not np.isnan(mcx_px) else "N/A"
gsr_now_str = f"{gsr_now:.1f}×" if not np.isnan(gsr_now) else "N/A"
inr_px_str = f"{inr_px:.2f}" if not np.isnan(inr_px) else "N/A"
dxy_px_str = f"{dxy_px:.2f}" if not np.isnan(dxy_px) else "N/A"
ry_now_str = f"{ry_now:+.2f}%" if not np.isnan(ry_now) else "N/A"

# determine card classes
ag_cls  = "bull" if ag_d1 and ag_d1 > 0 else ("bear" if ag_d1 and ag_d1 < 0 else "neu")
mcx_cls = "bull" if mcx_d1 and mcx_d1 > 0 else ("bear" if mcx_d1 and mcx_d1 < 0 else "neu")
dxy_cls = "bear" if dxy_above_200 else "bull"
inr_cls = "warn" if inr_d1 and inr_d1 > 0 else ("bull" if inr_d1 and inr_d1 < 0 else "neu")
ry_cls  = "bull" if (not np.isnan(ry_now) and ry_now < 0) else ("bear" if not np.isnan(ry_now) and ry_now > 1 else "warn")

kpi_html = f"""
<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:.75rem;margin-bottom:1.25rem;">

  <div class="kpi {ag_cls}">
    <div class="lbl">COMEX Silver</div>
    <div class="val" style="color:{SIL_GLOW};">{ag_px_str}</div>
    <div class="sub">/troy oz &nbsp; {chg_html(ag_d1)} 1d</div>
  </div>

  <div class="kpi {mcx_cls}">
    <div class="lbl">MCX Silver (Est.)</div>
    <div class="val" style="color:{BULL if mcx_d1 and mcx_d1>0 else BEAR};">{mcx_px_str}</div>
    <div class="sub">/kg incl. duty &nbsp; {chg_html(mcx_d1)}</div>
  </div>

  <div class="kpi {gsr_pill_cls}">
    <div class="lbl">Gold / Silver Ratio</div>
    <div class="val" style="color:{gsr_col};">{gsr_now_str}</div>
    <div class="sub">{pill(gsr_label.split()[0]+' '+gsr_label.split()[1] if len(gsr_label.split())>1 else gsr_label, gsr_pill_cls)}</div>
  </div>

  <div class="kpi {inr_cls}">
    <div class="lbl">USD / INR</div>
    <div class="val" style="color:{WARN};">{inr_px_str}</div>
    <div class="sub">1d {chg_html(inr_d1)} &nbsp; ↑INR weak = MCX ↑</div>
  </div>

  <div class="kpi {dxy_cls}">
    <div class="lbl">DXY Index</div>
    <div class="val" style="color:{BEAR if dxy_above_200 else BULL};">{dxy_px_str}</div>
    <div class="sub">{pill('ABOVE 200-DMA ↓ Ag' if dxy_above_200 else 'BELOW 200-DMA ↑ Ag', dxy_cls)}</div>
  </div>

  <div class="kpi {ry_cls}">
    <div class="lbl">US Real Yield 10yr</div>
    <div class="val" style="color:{BULL if ry_now<0 else BEAR};">{ry_now_str}</div>
    <div class="sub">{pill('NEGATIVE → Bullish Ag' if ry_now<0 else 'POSITIVE → Headwind', ry_cls)}</div>
  </div>

</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════
T_OV, T_CMX, T_MAC, T_FUN, T_GSR, T_TECH = st.tabs([
    "📊  Overview",
    "🔄  COMEX → MCX",
    "🌐  Macro Framework",
    "⚙️  Fundamentals",
    "⚖️  Gold / Silver Ratio",
    "📈  Technical Analysis",
])


# ───────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ───────────────────────────────────────────────────────────
with T_OV:
    st.markdown('<div class="sec">Market Structure Overview</div>', unsafe_allow_html=True)

    col_chart, col_panel = st.columns([3, 1], gap="medium")

    with col_chart:
        if not ag.empty:
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                row_heights=[0.72, 0.28], vertical_spacing=0.04,
            )
            up_c = [BULL if c >= o else BEAR
                    for c, o in zip(ag["Close"], ag["Open"])]

            fig.add_trace(go.Candlestick(
                x=ag.index, open=ag["Open"], high=ag["High"],
                low=ag["Low"],  close=ag["Close"],
                name="COMEX Ag", increasing_line_color=BULL,
                decreasing_line_color=BEAR,
                increasing_fillcolor=BULL, decreasing_fillcolor=BEAR,
            ), row=1, col=1)

            for span, clr, dash, lbl in [
                (20,  WARN,   "solid", "20-DMA"),
                (50,  ACCENT, "dot",   "50-DMA"),
                (200, SIL,    "dash",  "200-DMA"),
            ]:
                if len(ag) >= span:
                    fig.add_trace(go.Scatter(
                        x=ag.index, y=ag["Close"].rolling(span).mean(),
                        name=lbl, line=dict(color=clr, width=1.4, dash=dash)
                    ), row=1, col=1)

            fig.add_trace(go.Bar(
                x=ag.index, y=ag["Volume"],
                name="Volume", marker_color=up_c, opacity=0.55
            ), row=2, col=1)

            fig.update_layout(
                **CHART_BASE,
                title=dict(text="COMEX Silver Futures ($/oz) — 2-Year Daily",
                           font=dict(size=13, color=SIL_GLOW)),
                height=520,
                xaxis_rangeslider_visible=False,
                yaxis_title="$/oz", yaxis2_title="Volume",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_panel:
        st.markdown('<div class="sec">Signal Dashboard</div>', unsafe_allow_html=True)

        w_trend = "BULLISH" if ag_d20 and ag_d20 > 0 else "BEARISH"
        w_col   = "bull" if w_trend == "BULLISH" else "bear"

        signals_data = [
            ("Weekly Trend",   w_trend,              w_col),
            ("DXY vs 200-DMA", "BEARISH" if dxy_above_200 else "BULLISH",
             "bear" if dxy_above_200 else "bull"),
            ("Real Yield",     "BULLISH" if ry_now < 0 else ("NEUTRAL" if ry_now < 1 else "BEARISH"),
             "bull" if ry_now < 0 else ("warn" if ry_now < 1 else "bear")),
            ("GSR Signal",     gsr_label.split()[1] if len(gsr_label.split()) > 1 else gsr_label,
             gsr_pill_cls),
            ("Above 200-DMA",  "YES" if ag_above_200 else "NO",
             "bull" if ag_above_200 else "bear"),
            ("RSI(14)",
             f"OVERBOUGHT ({rsi_now:.0f})" if rsi_now > 70 else
             f"OVERSOLD ({rsi_now:.0f})" if rsi_now < 30 else
             f"NEUTRAL ({rsi_now:.0f})",
             "bear" if rsi_now > 70 else ("bull" if rsi_now < 30 else "warn")),
            ("BB Squeeze",     "ACTIVE ⚡" if squeeze else "NONE", "warn" if squeeze else "neu"),
            ("OBV Trend",      "RISING ↑" if obv_rising else ("FALLING ↓" if obv_rising is False else "—"),
             "bull" if obv_rising else ("bear" if obv_rising is False else "neu")),
            ("Macro Score",    f"{overall_macro} ({macro_score:+d}/5)", "bull" if macro_score > 0 else ("bear" if macro_score < 0 else "warn")),
        ]

        for name, sig, cls in signals_data:
            st.markdown(f"""
            <div class="sig-row">
              <span class="name">{name}</span>
              {pill(sig, cls)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec">52-Week Range</div>', unsafe_allow_html=True)

        if not ag.empty:
            h52 = float(ag["High"].tail(252).max())
            l52 = float(ag["Low"].tail(252).min())
            from_h = (ag_px - h52) / h52 * 100

            for lbl, val, vc in [
                ("52W High",   f"${h52:.2f}",         BEAR if from_h < -15 else WARN),
                ("52W Low",    f"${l52:.2f}",          BULL),
                ("Δ from ATH", f"{from_h:+.1f}%",     BEAR if from_h < -10 else WARN),
                ("MCX Est.",   f"₹{mcx_px:,.0f}/kg" if not np.isnan(mcx_px) else "N/A",  SIL_GLOW),
                ("USDINR",     f"{inr_px:.2f}" if not np.isnan(inr_px) else "N/A",        WARN),
                ("Copper",     f"${cu_px:.2f}" if not np.isnan(cu_px) else "N/A",        BULL if _pct(copper) and _pct(copper) > 0 else BEAR),
            ]:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:.35rem 0;
                            border-bottom:1px solid {GRID};font-size:.8rem;">
                  <span style="color:{MUTED};">{lbl}</span>
                  <span style="color:{vc};font-weight:600;">{val}</span>
                </div>""", unsafe_allow_html=True)

    # Correlation mini-chart
    if not ag.empty and not dxy.empty and not au.empty:
        st.markdown('<div class="sec" style="margin-top:1rem;">Asset Correlation (30-day Rolling vs Silver)</div>', unsafe_allow_html=True)

        base = ag["Close"].rename("Ag")
        corr_assets = {
            "Gold (GC=F)":   au["Close"],
            "DXY":           dxy["Close"],
            "USD/INR":       inr["Close"],
            "Copper (HG=F)": copper["Close"],
            "SLV ETF":       slv["Close"],
        }

        corr_rows = []
        for name_, ser in corr_assets.items():
            merged = base.align(ser, join="inner")
            roll_corr = merged[0].rolling(30).corr(merged[1]).dropna()
            if not roll_corr.empty:
                corr_rows.append({
                    "Asset": name_,
                    "30d Corr": float(roll_corr.iloc[-1]),
                    "3m Corr":  float(merged[0].tail(66).corr(merged[1].tail(66))) if len(merged[0]) >= 66 else np.nan,
                })

        df_corr = pd.DataFrame(corr_rows).dropna()
        if not df_corr.empty:
            fig_corr = go.Figure()
            fig_corr.add_trace(go.Bar(
                x=df_corr["Asset"],
                y=df_corr["30d Corr"],
                name="30d",
                marker_color=[BULL if v > 0 else BEAR for v in df_corr["30d Corr"]],
                text=[f"{v:+.2f}" for v in df_corr["30d Corr"]],
                textposition="outside", textfont=dict(size=10, color=TEXT),
            ))
            fig_corr.add_trace(go.Scatter(
                x=df_corr["Asset"], y=df_corr["3m Corr"],
                name="3m", mode="markers",
                marker=dict(size=10, color=WARN, symbol="diamond"),
            ))
            fig_corr.add_hline(y=0, line_color=MUTED, line_width=1)
            
            fig_corr.update_layout(
                **CHART_BASE,
                title=dict(text="30-Day Rolling Correlation with COMEX Silver (bars) vs 3-Month (◆)",
                           font=dict(size=12, color=SIL_GLOW)),
                height=280, 
                yaxis_range=[-1.1, 1.1],
                showlegend=True, 
                bargap=0.4,
            )
            st.plotly_chart(fig_corr, use_container_width=True)


# ───────────────────────────────────────────────────────────
# TAB 2 — COMEX → MCX
# ───────────────────────────────────────────────────────────
with T_CMX:
    st.markdown('<div class="sec">Live Price Bridge — COMEX ($/oz) → MCX (₹/kg)</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:.75rem;color:{MUTED};font-family:'IBM Plex Mono';margin-bottom:.75rem;">
      Formula: MCX (₹/kg) = COMEX ($/oz) × 32.1507 g/oz × USD/INR × (1 + Import Duty + Other Charges)
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    duty_pct = sc1.slider("Import Duty + Charges (%)", min_value=5, max_value=20, value=10, step=1)
    ov_comex = sc2.number_input("Override COMEX ($/oz)", value=round(ag_px, 2) if not np.isnan(ag_px) else 30.0, step=0.5)
    ov_inr   = sc3.number_input("Override USD/INR", value=round(inr_px, 2) if not np.isnan(inr_px) else 84.0, step=0.25)

    calc_mcx = mcx_est(ov_comex, ov_inr, duty_pct / 100)
    base_usd  = ov_comex * 32.1507
    conv_inr  = base_usd * ov_inr
    duty_add  = conv_inr * duty_pct / 100

    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {ACCENT}33;border-radius:12px;
                padding:1.4rem 2rem;margin:1rem 0;">
      <div style="display:flex;align-items:center;justify-content:center;
                  gap:1.5rem;flex-wrap:wrap;text-align:center;">
        <div>
          <div style="font-size:.65rem;color:{MUTED};text-transform:uppercase;letter-spacing:.1em;">COMEX Input</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:700;color:{SIL_GLOW};">
            ${ov_comex:,.2f}<span style="font-size:.9rem;color:{MUTED};">/oz</span>
          </div>
        </div>
        <div style="color:{MUTED};font-size:1.2rem;">→</div>
        <div>
          <div style="font-size:.65rem;color:{MUTED};text-transform:uppercase;letter-spacing:.1em;">× 32.1507 g/oz</div>
          <div style="font-size:1rem;color:{TEXT};">${base_usd:,.1f}/kg USD</div>
        </div>
        <div style="color:{MUTED};font-size:1.2rem;">→</div>
        <div>
          <div style="font-size:.65rem;color:{MUTED};text-transform:uppercase;letter-spacing:.1em;">× USD/INR {ov_inr:.2f}</div>
          <div style="font-size:1rem;color:{TEXT};">₹{conv_inr:,.0f}/kg</div>
        </div>
        <div style="color:{MUTED};font-size:1.2rem;">→</div>
        <div>
          <div style="font-size:.65rem;color:{MUTED};text-transform:uppercase;letter-spacing:.1em;">+ {duty_pct}% duty</div>
          <div style="font-size:1rem;color:{WARN};">+₹{duty_add:,.0f}</div>
        </div>
        <div style="color:{MUTED};font-size:1.2rem;">=</div>
        <div>
          <div style="font-size:.65rem;color:{MUTED};text-transform:uppercase;letter-spacing:.1em;">MCX Estimate</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:700;color:{BULL};">
            ₹{calc_mcx:,.0f}<span style="font-size:.9rem;color:{MUTED};">/kg</span>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        if not ag.empty and not inr.empty:
            merged_mcx = ag[["Close"]].join(inr[["Close"]], how="inner", rsuffix="_inr")
            merged_mcx.columns = ["comex", "usdinr"]
            merged_mcx["mcx_est"] = merged_mcx.apply(
                lambda r: mcx_est(r["comex"], r["usdinr"], duty_pct / 100), axis=1
            )

            fig_mcx = go.Figure()
            fig_mcx.add_trace(go.Scatter(
                x=merged_mcx.index, y=merged_mcx["mcx_est"],
                name="MCX Estimate ₹/kg",
                line=dict(color=SIL_GLOW, width=2.5),
                fill="tozeroy", fillcolor=f"rgba(200,212,240,0.06)",
            ))
            fig_mcx.add_trace(go.Scatter(
                x=merged_mcx.index,
                y=merged_mcx["mcx_est"].rolling(20).mean(),
                name="20-DMA", line=dict(color=WARN, width=1.5, dash="dash")
            ))
            fig_mcx.update_layout(
                **CHART_BASE,
                title=dict(text="Estimated MCX Silver Price (₹/kg) — Live Calculation",
                           font=dict(size=12, color=SIL_GLOW)),
                height=340, yaxis_title="₹/kg",
            )
            st.plotly_chart(fig_mcx, use_container_width=True)

    with col_b:
        if not inr.empty:
            fig_inr = go.Figure()
            fig_inr.add_trace(go.Scatter(
                x=inr.index, y=inr["Close"],
                name="USD/INR", line=dict(color=WARN, width=2),
            ))
            fig_inr.add_trace(go.Scatter(
                x=inr.index, y=inr["Close"].rolling(50).mean(),
                name="50-DMA", line=dict(color=ACCENT, width=1.5, dash="dash"),
            ))
            fig_inr.add_trace(go.Scatter(
                x=inr.index, y=inr["Close"].rolling(200).mean(),
                name="200-DMA", line=dict(color=SIL, width=1.5, dash="dot"),
            ))
            fig_inr.update_layout(
                **CHART_BASE,
                title=dict(text="USD / INR Exchange Rate — The Hidden MCX Variable",
                           font=dict(size=12, color=SIL_GLOW)),
                height=340, yaxis_title="INR per USD",
            )
            st.plotly_chart(fig_inr, use_container_width=True)

    # Waterfall decomposition
    if not np.isnan(ag_px) and not np.isnan(inr_px):
        base_comp = ag_px * 32.1507
        inr_comp  = base_comp * (inr_px - 1)
        duty_comp = (base_comp + inr_comp) * duty_pct / 100
        total_val = mcx_est(ag_px, inr_px, duty_pct / 100)

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["COMEX ($/oz × 32.15)", "FX Conversion", f"Duty ({duty_pct}%)", "MCX Total"],
            y=[base_comp, inr_comp, duty_comp, 0],
            text=[f"₹{base_comp:,.0f}", f"₹{inr_comp:,.0f}", f"₹{duty_comp:,.0f}", f"₹{total_val:,.0f}"],
            textposition="outside",
            textfont=dict(color=TEXT, size=11, family="IBM Plex Mono"),
            connector=dict(line=dict(color=GRID, width=1)),
            increasing=dict(marker=dict(color=BULL, line=dict(color=BULL, width=1))),
            decreasing=dict(marker=dict(color=BEAR, line=dict(color=BEAR, width=1))),
            totals=dict(marker=dict(color=ACCENT, line=dict(color=ACCENT, width=1))),
        ))
        fig_wf.update_layout(
            **CHART_BASE,
            title=dict(text="MCX Price Build-Up Waterfall (₹/kg)",
                       font=dict(size=12, color=SIL_GLOW)),
            height=320, showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown(f"""
    <div class="insight">
      💡 <strong>Rupee Amplification:</strong> A 1% INR depreciation adds ~1% to MCX silver with zero COMEX change.
      In 2013, COMEX fell 35% but MCX fell only 22% because the Rupee weakened 15% simultaneously.
      Always monitor COMEX direction AND USD/INR direction before every MCX trade.
    </div>
    """, unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# TAB 3 — MACRO FRAMEWORK
# ───────────────────────────────────────────────────────────
with T_MAC:
    st.markdown('<div class="sec">Five-Factor Macro Scorecard</div>', unsafe_allow_html=True)

    col_gauge, col_factors = st.columns([1, 2], gap="medium")

    with col_gauge:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=macro_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"Macro Score<br><span style='font-size:11px;color:{macro_col}'>{overall_macro}</span>",
                   "font": {"color": TEXT, "size": 14, "family": "Syne"}},
            number={"font": {"color": macro_col, "size": 40, "family": "Syne"}, "suffix": "/5"},
            gauge={
                "axis": {"range": [-5, 5], "tickcolor": MUTED,
                          "tickfont": {"color": MUTED, "size": 10}},
                "bar":  {"color": macro_col, "thickness": 0.25},
                "bgcolor": BG_MAIN,
                "bordercolor": GRID,
                "steps": [
                    {"range": [-5, -2], "color": "rgba(240, 64, 96, 0.15)"},
                    {"range": [-2,  2], "color": "rgba(240, 160, 48, 0.10)"},
                    {"range": [2,   5], "color": "rgba(34, 209, 138, 0.15)"},
                ],
                "threshold": {"line": {"color": WARN, "width": 2},
                               "thickness": 0.75, "value": 0},
            },
        ))
        fig_g.update_layout(paper_bgcolor=BG_CARD, font={"color": TEXT},
                             height=260, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig_g, use_container_width=True)

        st.markdown(f"""
        <div style="text-align:center;padding:.5rem;background:{BG_SURFACE};
                    border:1px solid {macro_col}44;border-radius:8px;
                    font-family:'Syne',sans-serif;font-size:.95rem;
                    font-weight:700;color:{macro_col};">
          {overall_macro}
        </div>
        """, unsafe_allow_html=True)

    with col_factors:
        st.markdown('<div class="sec">Factor Breakdown</div>', unsafe_allow_html=True)
        for name, score, detail in macro_rows:
            cls  = "bull" if score > 0 else ("bear" if score < 0 else "neu")
            icon = "▲" if score > 0 else ("▼" if score < 0 else "◈")
            c    = BULL if score > 0 else (BEAR if score < 0 else MUTED)
            lbl  = "Bullish" if score > 0 else ("Bearish" if score < 0 else "Neutral")
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        background:{BG_SURFACE};border:1px solid {GRID};
                        border-left:3px solid {c};border-radius:0 8px 8px 0;
                        padding:.65rem 1rem;margin:.35rem 0;">
              <div>
                <div style="font-size:.82rem;font-weight:600;color:{TEXT};">{name}</div>
                <div style="font-size:.72rem;color:{MUTED};margin-top:.15rem;">{detail}</div>
              </div>
              <span style="font-size:.8rem;color:{c};font-weight:700;">{icon} {lbl}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Chart row
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        if not dxy.empty:
            fig_dxy = go.Figure()
            fig_dxy.add_trace(go.Scatter(
                x=dxy.index, y=dxy["Close"],
                name="DXY", line=dict(color=ACCENT, width=2),
                fill="tozeroy", fillcolor=f"rgba(64,128,255,0.06)",
            ))
            if len(dxy) >= 200:
                fig_dxy.add_trace(go.Scatter(
                    x=dxy.index, y=dxy["Close"].rolling(200).mean(),
                    name="200-DMA", line=dict(color=WARN, width=1.5, dash="dash"),
                ))
            if not np.isnan(dxy_200):
                fig_dxy.add_annotation(
                    x=dxy.index[-1], y=dxy_200,
                    text=f"200-DMA {dxy_200:.1f}",
                    showarrow=False, font=dict(color=WARN, size=10),
                    bgcolor=BG_CARD, bordercolor=WARN, xanchor="right",
                )
            fig_dxy.add_annotation(
                text="DXY above 200-DMA = Silver headwind",
                x=0.02, y=0.95, xref="paper", yref="paper",
                showarrow=False, font=dict(color=BEAR, size=10),
                bgcolor=BG_CARD,
            ) if dxy_above_200 else fig_dxy.add_annotation(
                text="DXY below 200-DMA = Silver tailwind",
                x=0.02, y=0.95, xref="paper", yref="paper",
                showarrow=False, font=dict(color=BULL, size=10),
                bgcolor=BG_CARD,
            )
            fig_dxy.update_layout(
                **CHART_BASE,
                title=dict(text="US Dollar Index (DXY) — Inverse Silver Driver",
                           font=dict(size=12, color=SIL_GLOW)),
                height=330, yaxis_title="DXY",
            )
            st.plotly_chart(fig_dxy, use_container_width=True)

    with c2:
        if not tips.empty:
            fig_ry = go.Figure()
            ymin = float(tips["value"].min()) - 0.2
            if ymin < 0:
                fig_ry.add_hrect(
                    y0=ymin, y1=0,
                    fillcolor=f"rgba(34,209,138,0.07)", line_width=0,
                    annotation_text="Negative Real Yield → Silver Bullish",
                    annotation_font=dict(color=BULL, size=10),
                )
            fig_ry.add_trace(go.Scatter(
                x=tips.index, y=tips["value"],
                name="10yr TIPS Real Yield",
                line=dict(
                    color=BULL if ry_now < 0 else BEAR,
                    width=2.5
                ),
            ))
            fig_ry.add_hline(y=0, line_dash="dash", line_color=WARN,
                              line_width=1.5,
                              annotation_text="Zero Line",
                              annotation_font=dict(color=WARN, size=10))
            fig_ry.update_layout(
                **CHART_BASE,
                title=dict(text="US 10-Year Real Yield (TIPS, DFII10) — Primary Silver Driver",
                           font=dict(size=12, color=SIL_GLOW)),
                height=330, yaxis_title="Yield (%)",
            )
            st.plotly_chart(fig_ry, use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")

    with c3:
        if not tips.empty and not dgs10.empty and not t10yie.empty:
            fig_yd = go.Figure()
            for df_, nm, clr in [
                (dgs10,  "Nominal 10yr", ACCENT),
                (t10yie, "Breakeven Inflation", WARN),
                (tips,   "Real Yield",   BULL if ry_now < 0 else BEAR),
            ]:
                fig_yd.add_trace(go.Scatter(
                    x=df_.index, y=df_["value"],
                    name=nm, line=dict(color=clr, width=2),
                ))
            fig_yd.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=1)
            fig_yd.update_layout(
                **CHART_BASE,
                title=dict(text="Yield Decomposition: Nominal = Real + Breakeven Inflation",
                           font=dict(size=12, color=SIL_GLOW)),
                height=330, yaxis_title="Yield (%)",
            )
            st.plotly_chart(fig_yd, use_container_width=True)

    with c4:
        # DXY vs Silver scatter — colour coded by date
        if not ag.empty and not dxy.empty:
            joined = ag["Close"].align(dxy["Close"], join="inner")
            scatter_df = pd.DataFrame({"silver": joined[0], "dxy": joined[1]}).dropna()
            scatter_df["t"] = range(len(scatter_df))
            corr = scatter_df["silver"].corr(scatter_df["dxy"])

            fig_sc = go.Figure(go.Scatter(
                x=scatter_df["dxy"], y=scatter_df["silver"],
                mode="markers",
                marker=dict(
                    color=scatter_df["t"],
                    colorscale=[[0, BEAR], [0.5, MUTED], [1, BULL]],
                    size=5, opacity=0.75,
                    colorbar=dict(title="Time →", thickness=10, tickfont=dict(size=9, color=MUTED)),
                ),
                hovertemplate="DXY: %{x:.1f}<br>Silver: $%{y:.2f}<extra></extra>",
            ))
            fig_sc.update_layout(
                **CHART_BASE,
                title=dict(text=f"DXY vs COMEX Silver — Correlation: {corr:+.2f} (darker=older)",
                           font=dict(size=12, color=SIL_GLOW)),
                height=330,
                xaxis_title="DXY", yaxis_title="Silver ($/oz)",
            )
            st.plotly_chart(fig_sc, use_container_width=True)

    # Real yield impact table
    ry_table = {
        "Real Yield Zone": ["< −1% (Deeply Negative)", "−1% to 0% (Mildly Negative)", "0% to +0.5% (Near Zero)", "+0.5% to +2% (Positive)", "> +2% (Highly Positive)"],
        "Signal for Silver": ["🟢 STRONGLY BULLISH", "🟢 BULLISH", "🟡 NEUTRAL", "🔴 HEADWIND", "🔴 STRONG HEADWIND"],
        "Strategy": ["Full long bias. Add on corrections.", "Long bias. Standard size.", "No directional macro bias. Use technicals.", "Reduce longs. Tighten stops.", "Avoid longs. Short-term trades only."],
        "Current?": ["✓" if ry_now < -1 else "" , "✓" if -1 <= ry_now < 0 else "",
                      "✓" if 0 <= ry_now < 0.5 else "", "✓" if 0.5 <= ry_now < 2 else "",
                      "✓" if ry_now >= 2 else ""],
    }
    df_ry = pd.DataFrame(ry_table)
    st.markdown('<div class="sec" style="margin-top:.5rem;">Real Yield → Silver Signal Framework</div>', unsafe_allow_html=True)
    st.dataframe(df_ry, use_container_width=True, hide_index=True)


# ───────────────────────────────────────────────────────────
# TAB 4 — FUNDAMENTALS
# ───────────────────────────────────────────────────────────
with T_FUN:
    st.markdown(f"""
    <div class="warn-box">
      ⚠ Annual supply/demand data sourced from Silver Institute public reports (reference data).
      Price/ETF proxies are live.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sec">Supply, Demand & Structural Deficit</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")

    with c1:
        years = [2021, 2022, 2023, 2024, 2025]
        supply_m = [829, 847, 831, 820, 830]
        demand_m = [1020, 1240, 1120, 1160, 1180]
        deficit_m = [d - s for d, s in zip(demand_m, supply_m)]

        fig_sd = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sd.add_trace(go.Bar(
            x=years, y=supply_m, name="Mine Supply (M oz)",
            marker_color=f"rgba(64,128,255,0.75)", width=0.35,
            offset=-0.18,
        ), secondary_y=False)
        fig_sd.add_trace(go.Bar(
            x=years, y=demand_m, name="Total Demand (M oz)",
            marker_color=f"rgba(240,64,96,0.75)", width=0.35,
            offset=0.18,
        ), secondary_y=False)
        fig_sd.add_trace(go.Scatter(
            x=years, y=deficit_m, name="Deficit (M oz)",
            line=dict(color=WARN, width=3),
            mode="lines+markers+text",
            marker=dict(size=9, color=WARN),
            text=[f"{v}" for v in deficit_m],
            textposition="top center",
            textfont=dict(color=WARN, size=10),
        ), secondary_y=True)
        fig_sd.update_layout(
            **CHART_BASE,
            title=dict(text="Silver Supply vs Demand & Annual Deficit (M oz) — Silver Institute",
                       font=dict(size=12, color=SIL_GLOW)),
            height=340, barmode="group",
        )
        fig_sd.update_yaxes(title_text="Million oz", gridcolor=GRID, zeroline=False, secondary_y=False)
        fig_sd.update_yaxes(title_text="Deficit (M oz)", gridcolor=GRID, zeroline=False,
                             showgrid=False, secondary_y=True)
        st.plotly_chart(fig_sd, use_container_width=True)

    with c2:
        if not slv.empty:
            fig_slv = make_subplots(specs=[[{"secondary_y": True}]])
            fig_slv.add_trace(go.Scatter(
                x=slv.index, y=slv["Close"],
                name="SLV Price ($)", line=dict(color=SIL_GLOW, width=2),
                fill="tozeroy", fillcolor="rgba(200,212,240,0.05)",
            ), secondary_y=False)
            fig_slv.add_trace(go.Bar(
                x=slv.index, y=slv["Volume"],
                name="SLV Volume",
                marker_color=[BULL if c >= o else BEAR
                               for c, o in zip(slv["Close"], slv["Open"])],
                opacity=0.4,
            ), secondary_y=True)
            fig_slv.update_layout(
                **CHART_BASE,
                title=dict(text="SLV ETF — Investment Demand Proxy (Price + Volume)",
                           font=dict(size=12, color=SIL_GLOW)),
                height=340,
            )
            fig_slv.update_yaxes(title_text="Price ($)", gridcolor=GRID, zeroline=False, secondary_y=False)
            fig_slv.update_yaxes(title_text="Volume", gridcolor=GRID, zeroline=False,
                                  showgrid=False, secondary_y=True)
            st.plotly_chart(fig_slv, use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")

    with c3:
        sectors = ["Solar PV", "Electronics & Semi", "Electric Vehicles",
                   "AI / Data Centres", "Medical Devices",
                   "Jewellery & Silverware", "Investment (ETF/Bar)"]
        vals    = [29, 20, 10, 5, 4, 20, 12]
        s_clrs  = [WARN, ACCENT, BULL, "#a864ff", "#f07048", "#e8c050", SIL_GLOW]

        fig_pie = go.Figure(go.Pie(
            labels=sectors, values=vals, hole=0.52,
            marker=dict(colors=s_clrs, line=dict(color=BG_MAIN, width=2)),
            textinfo="label+percent",
            textfont=dict(size=10, color=TEXT, family="IBM Plex Mono"),
            hovertemplate="<b>%{label}</b><br>%{value}% of demand<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"Total<br><b style='font-size:18px'>~1.18B oz</b>",
            x=0.5, y=0.5, font=dict(size=12, color=TEXT, family="Syne"),
            showarrow=False,
        )
        fig_pie.update_layout(
            **CHART_BASE,
            title=dict(text="Silver Demand Mix by Sector (2024 est.) — Silver Institute",
                       font=dict(size=12, color=SIL_GLOW)),
            height=360, showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c4:
        solar_y  = [2014, 2016, 2018, 2020, 2022, 2024, 2026]
        solar_sh = [11, 14, 18, 21, 25, 29, 32]

        fig_sol = go.Figure()
        fig_sol.add_trace(go.Scatter(
            x=solar_y, y=solar_sh,
            name="Solar % of Industrial", line=dict(color=WARN, width=3),
            fill="tozeroy", fillcolor="rgba(240,160,48,0.09)",
            mode="lines+markers+text",
            marker=dict(size=8, color=WARN),
            text=[f"{v}%" for v in solar_sh],
            textposition="top center",
            textfont=dict(color=WARN, size=11),
        ))
        fig_sol.update_layout(
            **CHART_BASE,
            title=dict(text="Solar PV's Rising Share of Silver Industrial Demand (%)",
                       font=dict(size=12, color=SIL_GLOW)),
            height=360, yaxis_title="% of Industrial Demand",
            xaxis_dtick=2,
        )
        st.plotly_chart(fig_sol, use_container_width=True)

    # Mine supply + drivers table
    c5, c6 = st.columns(2, gap="medium")

    with c5:
        countries  = ["Mexico", "China", "Peru", "Chile", "Russia", "Australia", "Others"]
        supply_pct = [24, 14, 13, 10, 7, 6, 26]
        risk_lvl   = ["🔴 High (strikes)", "🟡 Opaque (state)",
                      "🔴 High (blockades)", "🟢 Stable",
                      "🔴 Sanctions", "🟢 Stable", "🟡 Mixed"]

        fig_mine = go.Figure(go.Bar(
            y=countries, x=supply_pct,
            orientation="h",
            marker=dict(
                color=[BEAR, WARN, BEAR, BULL, BEAR, BULL, MUTED],
                line=dict(color=BG_MAIN, width=1),
            ),
            text=[f"{v}%  {r}" for v, r in zip(supply_pct, risk_lvl)],
            textposition="inside",
            textfont=dict(size=10, color=TEXT),
        ))
        fig_mine.update_layout(
            **CHART_BASE,
            title=dict(text="Mine Supply by Country (% Global) + Disruption Risk",
                       font=dict(size=12, color=SIL_GLOW)),
            height=320, xaxis_title="% Share",
        )
        st.plotly_chart(fig_mine, use_container_width=True)

    with c6:
        drivers_df = pd.DataFrame({
            "Demand Sector":  ["Solar PV", "Electric Vehicles", "AI / Data Centres", "5G Networks", "Medical"],
            "2024 Share (%)": [29, 10, 5, 5, 4],
            "CAGR Outlook":   ["+8% to 2030", "+3.4% to 2031", "Explosive ↑↑", "+5% to 2028", "+2%"],
            "Key Catalyst":   ["EU 700GW 2030", "Global EV adoption", "Hyperscaler capex", "5G rollout", "Demographics"],
            "Signal":         ["BULLISH", "BULLISH", "STRONGLY BULLISH", "BULLISH", "NEUTRAL"],
        })

        def color_sig(v):
            if "STRONGLY" in v: return f"color: {BULL}; font-weight: bold;"
            if "BULLISH"  in v: return f"color: {BULL};"
            if "BEARISH"  in v: return f"color: {BEAR};"
            return f"color: {WARN};"

        st.markdown('<div class="sec">Industrial Demand Growth Vectors</div>', unsafe_allow_html=True)
        styled = drivers_df.style.map(color_sig, subset=["Signal"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="insight" style="margin-top:.75rem;">
          📌 <strong>Supply Inelasticity:</strong> 70–75% of silver is a by-product of copper/zinc/gold mining.
          New dedicated silver mines need 5–8 years from discovery to production. Five consecutive years
          of deficit (2021–2025) have <em>not</em> been resolved by higher prices — this is a structural floor.
        </div>
        """, unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# TAB 5 — GOLD / SILVER RATIO
# ───────────────────────────────────────────────────────────
with T_GSR:
    st.markdown('<div class="sec">Gold / Silver Ratio — The Contrarian Timing Tool</div>', unsafe_allow_html=True)

    if not ag.empty and not au.empty:
        gsr_live = (au["Close"] / ag["Close"]).dropna()
        gsr_cur  = float(gsr_live.iloc[-1])
        gsr_1m   = float(gsr_live.iloc[-22])  if len(gsr_live) > 22  else np.nan
        gsr_3m   = float(gsr_live.iloc[-66])  if len(gsr_live) > 66  else np.nan
        gsr_1y   = float(gsr_live.iloc[-252]) if len(gsr_live) > 252 else np.nan
        gsr_mean = float(gsr_live.mean())
        gsr_min  = float(gsr_live.min())
        gsr_max  = float(gsr_live.max())
    else:
        gsr_live = pd.Series(dtype=float)
        gsr_cur = gsr_1m = gsr_3m = gsr_1y = gsr_mean = gsr_min = gsr_max = np.nan

    gsr_lab, gsr_c, gsr_act, gsr_pc = gsr_interpret(gsr_cur)

    # KPI row
    kgc = st.columns(5)
    for col_, (lbl_, v_) in zip(kgc, [
        ("Current GSR",  f"{gsr_cur:.1f}×"),
        ("1-Month Ago",  f"{gsr_1m:.1f}×"  if not np.isnan(gsr_1m) else "—"),
        ("3-Month Ago",  f"{gsr_3m:.1f}×"  if not np.isnan(gsr_3m) else "—"),
        ("1-Year Ago",   f"{gsr_1y:.1f}×"  if not np.isnan(gsr_1y) else "—"),
        ("Period Mean",  f"{gsr_mean:.1f}×" if not np.isnan(gsr_mean) else "—"),
    ]):
        col_.markdown(f"""
        <div class="kpi {gsr_pc}">
          <div class="lbl">{lbl_}</div>
          <div class="val" style="color:{gsr_c};">{v_}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {gsr_c}44;
                border-left:4px solid {gsr_c};border-radius:0 10px 10px 0;
                padding:1rem 1.4rem;margin:.9rem 0;">
      <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:{gsr_c};">
        ⚖️ {gsr_lab}
      </div>
      <div style="font-size:.8rem;color:{TEXT};margin-top:.3rem;">
        📌 <strong>Action:</strong> {gsr_act}
      </div>
    </div>
    """, unsafe_allow_html=True)

    cg1, cg2 = st.columns([2, 1], gap="medium")

    with cg1:
        if not gsr_live.empty:
            fig_gsr = go.Figure()

            fig_gsr.add_hrect(y0=80, y1=float(gsr_live.max()) + 10,
                               fillcolor=f"rgba(34,209,138,0.06)", line_width=0)
            fig_gsr.add_annotation(
                x=gsr_live.index[len(gsr_live)//8], y=85,
                text="BUY SILVER ZONE (GSR > 80)",
                font=dict(color=BULL, size=10), showarrow=False,
            )
            fig_gsr.add_hrect(y0=0, y1=45,
                               fillcolor=f"rgba(240,64,96,0.06)", line_width=0)
            fig_gsr.add_annotation(
                x=gsr_live.index[len(gsr_live)//8], y=40,
                text="FAVOUR GOLD ZONE (GSR < 45)",
                font=dict(color=BEAR, size=10), showarrow=False,
            )

            fig_gsr.add_trace(go.Scatter(
                x=gsr_live.index, y=gsr_live,
                name="Gold/Silver Ratio",
                line=dict(color=GOLD_C, width=2.5),
            ))
            fig_gsr.add_trace(go.Scatter(
                x=gsr_live.index, y=gsr_live.rolling(50).mean(),
                name="50-DMA", line=dict(color=SIL, width=1.5, dash="dash"),
            ))
            fig_gsr.add_hline(y=gsr_mean, line_dash="dash", line_color=MUTED,
                               line_width=1,
                               annotation_text=f"Period Mean: {gsr_mean:.1f}",
                               annotation_font=dict(color=MUTED, size=10))
            fig_gsr.add_trace(go.Scatter(
                x=[gsr_live.index[-1]], y=[gsr_cur],
                mode="markers+text",
                marker=dict(size=14, color=gsr_c, symbol="circle"),
                text=[f"  {gsr_cur:.1f}"],
                textfont=dict(color=gsr_c, size=13, family="Syne"),
                name="Now",
            ))
            fig_gsr.update_layout(
                **CHART_BASE,
                title=dict(text=f"Live Gold/Silver Ratio — Current: {gsr_cur:.1f}×  |  Mean: {gsr_mean:.1f}×",
                           font=dict(size=13, color=SIL_GLOW)),
                height=420, yaxis_title="oz Silver per oz Gold",
            )
            st.plotly_chart(fig_gsr, use_container_width=True)

    with cg2:
        st.markdown('<div class="sec">GSR Signal Ladder</div>', unsafe_allow_html=True)
        ladder = [
            ("> 90", "Historic Extreme",    "MAX silver longs",       BULL,  lambda g: g > 90),
            ("80–90", "Deeply Undervalued", "Full silver bias",        BULL,  lambda g: 80 <= g <= 90),
            ("60–80", "Mildly Undervalued", "Standard allocation",     WARN,  lambda g: 60 <= g < 80),
            ("45–60", "Near Mean",          "Neutral. Use technicals", WARN,  lambda g: 45 <= g < 60),
            ("<  45", "Silver Pricey",      "Lean to gold",            BEAR,  lambda g: 35 <= g < 45),
            ("<  35", "Historic Extreme",   "Avoid Ag. Buy Au.",       BEAR,  lambda g: g < 35),
        ]
        for lvl, meaning, act, c_, chk in ladder:
            is_now = not np.isnan(gsr_cur) and chk(gsr_cur)
            bd     = f"border:1.5px solid {c_};" if is_now else f"border:1px solid {GRID};"
            bg     = f"background:{c_}18;" if is_now else f"background:{BG_SURFACE};"
            marker = f'<span style="font-size:.65rem;color:{c_};background:{c_}22;padding:.1rem .35rem;border-radius:4px;border:1px solid {c_};">◄ NOW</span>' if is_now else ""
            st.markdown(f"""
            <div style="{bd}{bg}border-radius:8px;padding:.6rem .8rem;margin:.3rem 0;">
              <div style="display:flex;align-items:center;justify-content:space-between;">
                <span style="color:{c_};font-weight:700;font-size:.85rem;">GSR {lvl}</span>
                {marker}
              </div>
              <div style="font-size:.75rem;color:{TEXT};margin-top:.1rem;">{meaning}</div>
              <div style="font-size:.7rem;color:{MUTED};font-style:italic;">{act}</div>
            </div>
            """, unsafe_allow_html=True)

    # Gold vs Silver relative performance
    st.markdown('<div class="sec" style="margin-top:.75rem;">Gold vs Silver — Indexed Performance (2yr)</div>', unsafe_allow_html=True)
    if not ag.empty and not au.empty:
        ag_n  = ag["Close"] / float(ag["Close"].iloc[0]) * 100
        au_n  = au["Close"] / float(au["Close"].iloc[0]) * 100

        fig_rel = go.Figure()
        fig_rel.add_trace(go.Scatter(
            x=ag_n.index, y=ag_n, name="Silver",
            line=dict(color=SIL_GLOW, width=2.5),
        ))
        fig_rel.add_trace(go.Scatter(
            x=au_n.index, y=au_n, name="Gold",
            line=dict(color=GOLD_C, width=2.5),
        ))
        fig_rel.add_hline(y=100, line_dash="dot", line_color=MUTED, line_width=1)

        last_ag = float(ag_n.iloc[-1])
        last_au = float(au_n.iloc[-1])
        winner  = "Silver" if last_ag > last_au else "Gold"
        w_col   = SIL_GLOW if winner == "Silver" else GOLD_C

        fig_rel.add_annotation(
            x=ag_n.index[-1], y=last_ag,
            text=f"  Ag: {last_ag:.0f}",
            showarrow=False, font=dict(color=SIL_GLOW, size=11), xanchor="left",
        )
        fig_rel.add_annotation(
            x=au_n.index[-1], y=last_au,
            text=f"  Au: {last_au:.0f}",
            showarrow=False, font=dict(color=GOLD_C, size=11), xanchor="left",
        )
        fig_rel.update_layout(
            **CHART_BASE,
            title=dict(text=f"Indexed Performance (Base=100) — Outperformer: {winner}",
                       font=dict(size=12, color=w_col)),
            height=300, yaxis_title="Indexed (Start = 100)",
        )
        st.plotly_chart(fig_rel, use_container_width=True)


# ───────────────────────────────────────────────────────────
# TAB 6 — TECHNICAL ANALYSIS
# ───────────────────────────────────────────────────────────
with T_TECH:
    st.markdown('<div class="sec">Technical Analysis — RSI · Bollinger Bands · OBV</div>', unsafe_allow_html=True)

    tfc, pdc = st.columns([1, 4])
    tf_sel   = tfc.selectbox("Timeframe", ["6mo", "1y", "2y"], index=1, label_visibility="collapsed")

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_tf(tf):
        df = _yf("SI=F", tf)
        return df

    tech = fetch_tf(tf_sel)

    if not tech.empty:
        cl = tech["Close"]
        vo = tech["Volume"]

        rsi_t  = calc_rsi(cl)
        bu, bm, bl = calc_bb(cl)
        bw     = ((bu - bl) / bm * 100)
        obv_t  = calc_obv(cl, vo)

        r_now  = float(rsi_t.dropna().iloc[-1])
        bp_now = float((cl.iloc[-1] - bl.iloc[-1]) / (bu.iloc[-1] - bl.iloc[-1]) * 100)
        bw_now = float(bw.dropna().tail(5).mean())
        bw_avg = float(bw.dropna().tail(60).mean())
        sq_now = bw_now < bw_avg * 0.70

        obv_r  = float(obv_t.iloc[-1]) > float(obv_t.iloc[-20]) if len(obv_t) > 20 else None

        # check divergence (30-bar window)
        rsi30  = rsi_t.dropna().tail(30)
        cl30   = cl.tail(30)
        b_div  = len(rsi30) == 30 and cl30.iloc[-1] < cl30.iloc[0] and rsi30.iloc[-1] > rsi30.iloc[0]
        bear_d = len(rsi30) == 30 and cl30.iloc[-1] > cl30.iloc[0] and rsi30.iloc[-1] < rsi30.iloc[0]

        # ── indicator signal cards ───────────────────────────
        ic = st.columns(5)
        ind_cards = [
            ("RSI (14)", f"{r_now:.1f}",
             "OVERBOUGHT" if r_now > 70 else ("OVERSOLD" if r_now < 30 else "NEUTRAL"),
             BEAR if r_now > 70 else (BULL if r_now < 30 else WARN)),
            ("RSI Divergence",
             "BULL DIV ▲" if b_div else ("BEAR DIV ▼" if bear_d else "NONE"),
             "30-bar check",
             BULL if b_div else (BEAR if bear_d else MUTED)),
            ("BB Position", f"{bp_now:.0f}%",
             "Upper Band" if bp_now > 75 else ("Lower Band" if bp_now < 25 else "Mid Range"),
             WARN if bp_now > 75 else (BULL if bp_now < 25 else MUTED)),
            ("BB Squeeze",
             "⚡ ACTIVE" if sq_now else "INACTIVE",
             f"Width {bw_now:.1f}% vs avg {bw_avg:.1f}%",
             WARN if sq_now else MUTED),
            ("OBV Trend",
             "RISING ↑" if obv_r else ("FALLING ↓" if obv_r is False else "—"),
             "20-bar direction",
             BULL if obv_r else (BEAR if obv_r is False else MUTED)),
        ]
        for c_, (t_, v_, s_, co_) in zip(ic, ind_cards):
            c_.markdown(f"""
            <div class="kpi" style="border-color:{co_}44;">
              <div class="lbl">{t_}</div>
              <div class="val" style="color:{co_};font-size:1.15rem;">{v_}</div>
              <div class="sub" style="color:{co_};opacity:.75;margin-top:.15rem;">{s_}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── main 4-panel chart ───────────────────────────────
        fig_t = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            row_heights=[0.50, 0.18, 0.18, 0.14],
            vertical_spacing=0.025,
            subplot_titles=[
                "COMEX Silver + Bollinger Bands (20,2) + 200-DMA",
                "RSI (14) — Divergence Monitor",
                "OBV — On-Balance Volume (Institutional Accumulation)",
                "BB Width — Squeeze Detector",
            ],
        )

        # Candles
        fig_t.add_trace(go.Candlestick(
            x=tech.index, open=tech["Open"], high=tech["High"],
            low=tech["Low"], close=cl, name="Ag",
            increasing_line_color=BULL, decreasing_line_color=BEAR,
            increasing_fillcolor=BULL, decreasing_fillcolor=BEAR,
        ), row=1, col=1)

        # Bollinger Bands
        fig_t.add_trace(go.Scatter(
            x=tech.index, y=bu, name="BB Upper",
            line=dict(color=ACCENT, width=1.2, dash="dash"), showlegend=True,
        ), row=1, col=1)
        fig_t.add_trace(go.Scatter(
            x=tech.index, y=bm, name="BB Mid (20-MA)",
            line=dict(color=WARN, width=1.6), showlegend=True,
        ), row=1, col=1)
        fig_t.add_trace(go.Scatter(
            x=tech.index, y=bl, name="BB Lower",
            line=dict(color=ACCENT, width=1.2, dash="dash"),
            fill="tonexty", fillcolor="rgba(64,128,255,0.05)",
            showlegend=True,
        ), row=1, col=1)

        if len(cl) >= 200:
            fig_t.add_trace(go.Scatter(
                x=tech.index, y=cl.rolling(200).mean(),
                name="200-DMA", line=dict(color=SIL, width=1.5, dash="dot"),
                showlegend=True,
            ), row=1, col=1)

        # RSI
        rsi_col_line = BEAR if r_now > 70 else (BULL if r_now < 30 else WARN)
        fig_t.add_trace(go.Scatter(
            x=rsi_t.index, y=rsi_t, name="RSI(14)",
            line=dict(color=rsi_col_line, width=2), showlegend=False,
        ), row=2, col=1)
        for lvl, c_ in [(70, BEAR), (50, MUTED), (30, BULL)]:
            fig_t.add_hline(y=lvl, line_dash="dash", line_color=c_,
                             line_width=1.2, row=2, col=1)
        fig_t.add_hrect(y0=70, y1=100, fillcolor=f"rgba(240,64,96,0.07)",  line_width=0, row=2, col=1)
        fig_t.add_hrect(y0=0,  y1=30,  fillcolor=f"rgba(34,209,138,0.07)", line_width=0, row=2, col=1)

        # OBV
        obv_c = BULL if obv_r else BEAR
        fig_t.add_trace(go.Scatter(
            x=obv_t.index, y=obv_t, name="OBV",
            line=dict(color=obv_c, width=2), showlegend=False,
            fill="tozeroy", fillcolor=f"rgba({'34,209,138' if obv_r else '240,64,96'},0.07)",
        ), row=3, col=1)
        fig_t.add_trace(go.Scatter(
            x=obv_t.index, y=obv_t.rolling(20).mean(), name="OBV 20-MA",
            line=dict(color=WARN, width=1.5, dash="dash"), showlegend=False,
        ), row=3, col=1)

        # BB Width
        fig_t.add_trace(go.Scatter(
            x=bw.index, y=bw, name="BB Width",
            line=dict(color=WARN, width=1.5), showlegend=False,
            fill="tozeroy", fillcolor="rgba(240,160,48,0.07)",
        ), row=4, col=1)
        if not np.isnan(bw_avg):
            fig_t.add_hline(y=bw_avg * 0.70, line_dash="dash", line_color=BEAR,
                             line_width=1.5, row=4, col=1,
                             annotation_text="Squeeze Threshold",
                             annotation_font=dict(color=BEAR, size=9))

        fig_t.update_layout(
            **CHART_BASE,
            height=880,
            xaxis_rangeslider_visible=False,
            title=dict(text="Complete Technical Dashboard — COMEX Silver Futures",
                       font=dict(size=13, color=SIL_GLOW)),
            showlegend=True,
        )
        for i in range(1, 5):
            fig_t.update_yaxes(gridcolor=GRID, zeroline=False, row=i, col=1,
                                tickfont=dict(color=MUTED, size=9))
        st.plotly_chart(fig_t, use_container_width=True)

        # ── Signal summary table ─────────────────────────────
        st.markdown('<div class="sec">Technical Signal Summary</div>', unsafe_allow_html=True)

        ab200 = not np.isnan(ag_200) and ag_px > ag_200
        sig_rows = [
            ("RSI Level",      f"{r_now:.1f}",
             "OVERBOUGHT — not a sell signal in strong uptrend; wait for divergence" if r_now > 70
             else "OVERSOLD — high-conviction buy zone if weekly trend supports" if r_now < 30
             else "Neutral — no strong momentum bias",
             BEAR if r_now > 70 else (BULL if r_now < 30 else WARN)),
            ("RSI Divergence", "BULL DIV (30-bar)" if b_div else ("BEAR DIV (30-bar)" if bear_d else "None detected"),
             "Bullish: price lower low + RSI higher low = high-conviction reversal entry signal",
             BULL if b_div else (BEAR if bear_d else MUTED)),
            ("BB Position",    f"{bp_now:.0f}% of band",
             "Price 'walking' upper band in uptrend is NOT a sell — wait for RSI divergence to fade longs",
             WARN if bp_now > 75 else (BULL if bp_now < 25 else MUTED)),
            ("BB Squeeze",     "ACTIVE ⚡" if sq_now else "Inactive",
             "Squeeze = volatility compression before explosive move. Trade the DIRECTION of the breakout.",
             WARN if sq_now else MUTED),
            ("OBV Trend",      "Rising ↑" if obv_r else ("Falling ↓" if obv_r is False else "—"),
             "Rising OBV + flat/falling price = 'Quiet Storm' = institutional accumulation before breakout",
             BULL if obv_r else (BEAR if obv_r is False else MUTED)),
            ("200-DMA",        f"{'ABOVE' if ab200 else 'BELOW'} ({ag_200:.2f})" if not np.isnan(ag_200) else "—",
             "Price above 200-DMA = structural bull market. The weekly trend is your directional bible.",
             BULL if ab200 else BEAR),
        ]
        for nm, vl, desc, co_ in sig_rows:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:1rem;
                        background:{BG_SURFACE};border:1px solid {GRID};
                        border-left:3px solid {co_};border-radius:0 8px 8px 0;
                        padding:.7rem 1rem;margin:.35rem 0;">
              <div style="min-width:170px;flex-shrink:0;">
                <div style="font-size:.8rem;color:{MUTED};">{nm}</div>
                <div style="font-size:.95rem;font-weight:700;color:{co_};font-family:'Syne',sans-serif;">{vl}</div>
              </div>
              <div style="font-size:.78rem;color:{TEXT};line-height:1.6;padding-top:.15rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("⚠ Could not fetch silver data. Please check your internet connection.")

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;color:{MUTED};font-size:.7rem;
            padding:1.25rem 0;margin-top:1.5rem;border-top:1px solid {GRID};">
  ⚠️ <strong>Disclaimer:</strong> Educational and analytical purposes only. Not financial advice.
  Silver trading involves significant risk of loss. Data: Yahoo Finance, FRED (St. Louis Fed),
  Silver Institute public reports. Refresh every 5 minutes.
  &nbsp;|&nbsp; Last render: {datetime.now().strftime("%d %b %Y %H:%M:%S IST")}
</div>
""", unsafe_allow_html=True)
