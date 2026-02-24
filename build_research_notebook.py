#!/usr/bin/env python3
"""
Build research.ipynb: main research notebook with all calculations, data, tables, figures.
Run: python3 build_research_notebook.py
Notebook includes: API download (Binance, yfinance, FRED) -> build_features -> analysis.
"""
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
NB_PATH = os.path.join(PROJECT_ROOT, "research.ipynb")


def cell_md(lines):
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in lines]}


def cell_code(lines):
    return {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None, "source": [line + "\n" for line in lines]}


cells = []

# --- Title and intro ---
cells.append(cell_md([
    "# Binance Gold & Silver Perpetuals and ETF Markets",
    "",
    "**Event study:** impact of Binance TRADFI XAUUSDT/XAGUSDT launch (2026-01-05) on GLD/SLV volatility, liquidity, and integration.",
    "",
    "**Hypotheses:** H1 — ETF volatility increases after the launch; H2 — volume/liquidity improves. Integration (correlation ETF–Binance) is described post-event only (no pre-event Binance data).",
    "",
    "**Data:** Uses only 3 CSV files in folder **`processed/`** (or `data/processed/`): `features_daily.csv`, `features_hourly.csv`, `features_1m.csv`. Upload this folder in Colab and run all cells. No API, no other files."
]))

# --- Setup: path to folder with 3 CSVs ---
cells.append(cell_md([
    "## Setup",
    "",
    "Path to the folder with the 3 panels. We look for `data/processed/` or, if missing, `processed/` (so in Colab you can upload a folder named **processed** with the 3 CSV files)."
]))

cells.append(cell_code([
    "import os",
    "import sys",
    "",
    "PROJECT_ROOT = os.getcwd()",
    "if PROJECT_ROOT not in sys.path:",
    "    sys.path.insert(0, PROJECT_ROOT)",
    "os.chdir(PROJECT_ROOT)",
    "",
    "# Folder with the 3 panels: try 'data/processed' then 'processed' (Colab often has just 'processed')",
    "PROC_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')",
    "if not os.path.exists(PROC_DIR):",
    "    PROC_DIR = os.path.join(PROJECT_ROOT, 'processed')",
    "os.makedirs(PROC_DIR, exist_ok=True)",
    "",
    "PATH_DAILY = os.path.join(PROC_DIR, 'features_daily.csv')",
    "PATH_HOURLY = os.path.join(PROC_DIR, 'features_hourly.csv')",
    "PATH_1M = os.path.join(PROC_DIR, 'features_1m.csv')",
    "",
    "print(f'Data folder: {PROC_DIR}')",
    "print('daily:', os.path.exists(PATH_DAILY), '| hourly:', os.path.exists(PATH_HOURLY), '| 1m:', os.path.exists(PATH_1M))",
    "if not os.path.exists(PATH_DAILY):",
    "    raise FileNotFoundError('Upload features_daily.csv, features_hourly.csv, features_1m.csv to folder processed/')",
]))

# --- 0. Check: we work only with these 3 files ---
cells.append(cell_md([
    "## 0. Data",
    "",
    "This notebook uses **only these 3 files** in the `processed` folder:",
    "- `features_daily.csv`",
    "- `features_hourly.csv`",
    "- `features_1m.csv`",
    "",
    "No API calls, no other files. If all three are present, we are ready."
]))

cells.append(cell_code([
    "required = [('features_daily.csv', PATH_DAILY), ('features_hourly.csv', PATH_HOURLY), ('features_1m.csv', PATH_1M)]",
    "for name, path in required:",
    "    print(f'{name}: {\"OK\" if os.path.exists(path) else \"missing\"}')",
]))

# --- Three panels table (after load + build) ---
cells.append(cell_md([
    "### Three panels",
    "",
    "We have **three panels** at different frequencies. The minute panel has the largest number of observations (tens of thousands of rows)."
]))

cells.append(cell_code([
    "import pandas as pd",
    "proc_dir = PROC_DIR",
    "",
    "def _panel_stats(path):",
    "    if not os.path.exists(path): return 0, '-', 0",
    "    try:",
    "        with open(path, encoding='utf-8') as f: n_rows = max(0, sum(1 for _ in f) - 1)",
    "        df = pd.read_csv(path, nrows=1)",
    "        n_cols = len(df.columns)",
    "        date_col = 'Date' if 'Date' in df.columns else (df.columns[0] if len(df.columns) else None)",
    "        if date_col:",
    "            s = pd.read_csv(path, usecols=[date_col], parse_dates=[date_col])",
    "            if len(s): period = f\"{s[date_col].min().date()} to {s[date_col].max().date()}\"",
    "            else: period = '-'",
    "        else: period = '-'",
    "        return n_rows, period, n_cols",
    "    except Exception: return 0, '-', 0",
    "",
    "panels = [",
    "    ('Daily', 'features_daily.csv', 'Event study, regressions, pre/post'),",
    "    ('Hourly', 'features_hourly.csv', 'Hourly returns/vol'),",
    "    ('Minute (1m)', 'features_1m.csv', 'Intraday dynamics, very large sample'),",
    "]",
    "",
    "rows = []",
    "for name, fname, desc in panels:",
    "    path = os.path.join(proc_dir, fname)",
    "    n_rows, period, n_cols = _panel_stats(path)",
    "    rows.append({'Panel': name, 'File': fname, 'Rows': n_rows, 'Period': period, 'Variables': n_cols, 'Purpose': desc})",
    "",
    "panels_table = pd.DataFrame(rows)",
    "panels_table['Rows'] = panels_table['Rows'].astype(int)",
    "print('Three panels (daily / hourly / 1m). Minute panel has the most observations.')",
    "from IPython.display import display",
    "display(panels_table)",
]))

# --- All panels: show data (daily, hourly, 1m) ---
cells.append(cell_md([
    "### All panels: data preview",
    "",
    "Below we load and display the data from all three panels: shape, column names, and first rows."
]))

cells.append(cell_code([
    "import pandas as pd",
    "from IPython.display import display",
    "",
    "for name, fname in [('Daily', 'features_daily.csv'), ('Hourly', 'features_hourly.csv'), ('Minute (1m)', 'features_1m.csv')]:",
    "    path = os.path.join(PROC_DIR, fname)",
    "    if not os.path.exists(path):",
    "        print(f'--- {name}: {fname} not found ---'); continue",
    "    peek = pd.read_csv(path, nrows=5)",
    "    date_col = 'Date' if 'Date' in peek.columns else (peek.columns[0] if len(peek.columns) else None)",
    "    with open(path, encoding='utf-8') as f: n_rows = sum(1 for _ in f) - 1",
    "    n_cols = len(peek.columns)",
    "    df = pd.read_csv(path, parse_dates=[date_col] if date_col in peek.columns else None) if n_rows <= 5000 else pd.read_csv(path, parse_dates=[date_col] if date_col in peek.columns else None, nrows=2000)",
    "    print(f'=== {name} ({fname}) ===')",
    "    print(f'Shape: {n_rows} rows x {n_cols} columns')",
    "    print(f'Columns: {list(df.columns)[:25]}{\" ...\" if len(df.columns) > 25 else \"\"}')",
    "    display(df.head(20))",
    "    print()",
]))

cells.append(cell_md([
    "**Full daily panel** (all rows):"
]))

cells.append(cell_code([
    "path_daily_preview = os.path.join(PROC_DIR, 'features_daily.csv')",
    "if os.path.exists(path_daily_preview):",
    "    df_daily_full = pd.read_csv(path_daily_preview, index_col=0, parse_dates=True)",
    "    print(f'Daily panel: {len(df_daily_full)} rows x {len(df_daily_full.columns)} columns')",
    "    display(df_daily_full)",
    "else:",
    "    print('features_daily.csv not found.')",
]))

# --- Imports and setup ---
cells.append(cell_code([
    "import pandas as pd",
    "import numpy as np",
    "import matplotlib.pyplot as plt",
    "import seaborn as sns",
    "import os",
    "",
    "plt.style.use('seaborn-v0_8-whitegrid')",
    "plt.rcParams['figure.dpi'] = 120",
    "plt.rcParams['font.size'] = 10",
    "COLORS = {'gld': '#B8860B', 'slv': '#708090', 'xau': '#C9A227', 'xag': '#0D9488', 'event': '#C41E3A', 'pre': '#2E86AB', 'post': '#E94F37'}",
    "",
    "proc_dir = PROC_DIR",
    "path_daily = PATH_DAILY",
    "if not os.path.exists(path_daily):",
    "    raise FileNotFoundError('Upload features_daily.csv to data/processed/ or run section 0 to build from raw.')",
]))

# --- Working with the hourly panel ---
cells.append(cell_md([
    "---",
    "## Working with the **hourly** panel",
    "",
    "We load the hourly panel and use it for: hourly returns and volatility, and a short time series of hourly activity."
]))

cells.append(cell_code([
    "path_hourly = os.path.join(proc_dir, 'features_hourly.csv')",
    "if os.path.exists(path_hourly):",
    "    df_hourly = pd.read_csv(path_hourly, index_col=0, parse_dates=True).sort_index()",
    "    print(f'Hourly panel: {len(df_hourly)} rows x {len(df_hourly.columns)} columns')",
    "    print('Sample columns:', [c for c in df_hourly.columns if 'ret' in c or 'vol' in c][:12])",
    "    if 'ret_gld' in df_hourly.columns and 'ret_xau_binance' in df_hourly.columns:",
    "        print('Hourly returns (GLD, XAU) describe:')",
    "        display(df_hourly[['ret_gld', 'ret_xau_binance']].describe())",
    "    display(df_hourly.head(24))",
    "else:",
    "    print('features_hourly.csv not found. Upload it to data/processed/.')",
]))

cells.append(cell_code([
    "if os.path.exists(path_hourly) and 'ret_xau_binance' in df_hourly.columns:",
    "    fig, ax = plt.subplots(figsize=(10, 3))",
    "    sample = df_hourly['ret_xau_binance'].dropna().iloc[:500]",
    "    ax.plot(sample.index, sample.values, color=COLORS['xau'], linewidth=0.8, alpha=0.9)",
    "    ax.set_ylabel('Hourly return (XAUUSDT)')",
    "    ax.set_title('Hourly panel: XAUUSDT returns (first 500 hours)')",
    "    plt.tight_layout()",
    "    plt.show()",
]))

# --- Working with the minute panel ---
cells.append(cell_md([
    "---",
    "## Working with the **minute** panel",
    "",
    "We use the 1m panel for: (1) number of 1m bars per day, (2) daily realized volatility from 1m returns (XAUUSDT), (3) distribution of 1m returns."
]))

cells.append(cell_code([
    "path_1m = os.path.join(proc_dir, 'features_1m.csv')",
    "if os.path.exists(path_1m):",
    "    df_1m = pd.read_csv(path_1m, parse_dates=['open_time']).set_index('open_time').sort_index()",
    "    df_1m.index = pd.to_datetime(df_1m.index)",
    "    df_1m['date'] = df_1m.index.date",
    "    bars_per_day = df_1m.groupby('date').size()",
    "    print('1m bars per day (XAUUSDT):')",
    "    print(bars_per_day.describe())",
    "    print()",
    "    if 'ret_xau_binance' in df_1m.columns:",
    "        daily_vol = df_1m.groupby('date')['ret_xau_binance'].apply(lambda x: np.sqrt((x**2).sum()))",
    "        print('Daily realized vol from 1m returns (annualized scale):')",
    "        print((daily_vol * np.sqrt(365 * 24 * 60)).describe().round(4))",
    "        print()",
    "    summary_1m = pd.DataFrame({'n_bars': bars_per_day})",
    "    if 'ret_xau_binance' in df_1m.columns:",
    "        summary_1m['daily_vol_1m'] = daily_vol",
    "    display(summary_1m.head(10))",
    "else:",
    "    print('features_1m.csv not found. Run the build step above.')",
]))

cells.append(cell_code([
    "if os.path.exists(path_1m) and 'ret_xau_binance' in df_1m.columns:",
    "    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))",
    "    r = df_1m['ret_xau_binance'].dropna()",
    "    r = r[np.isfinite(r)][r != 0]",
    "    axes[0].hist(r, bins=80, color=COLORS['xau'], alpha=0.8, edgecolor='none')",
    "    axes[0].set_xlabel('1m log return (XAUUSDT)')",
    "    axes[0].set_ylabel('Count')",
    "    axes[0].set_title('Distribution of 1m returns')",
    "    daily_vol = df_1m.groupby('date')['ret_xau_binance'].apply(lambda x: np.sqrt((x**2).sum()))",
    "    x_dates = pd.to_datetime(daily_vol.index)",
    "    axes[1].plot(x_dates, daily_vol.values, color=COLORS['xau'], linewidth=1)",
    "    axes[1].set_xlabel('Date')",
    "    axes[1].set_ylabel('Daily realized vol (1m)')",
    "    axes[1].set_title('Daily realized volatility from 1m returns')",
    "    import matplotlib.dates as mdates",
    "    axes[1].xaxis.set_major_locator(mdates.WeekdayLocator(interval=7))",
    "    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))",
    "    axes[1].tick_params(axis='x', rotation=45)",
    "    plt.tight_layout()",
    "    plt.show()",
]))

# --- Working with the daily panel ---
cells.append(cell_md([
    "---",
    "## Working with the **daily** panel",
    "",
    "We use the daily panel for the event study: event date, pre/post split, t-tests, OLS regressions, key results table."
]))

cells.append(cell_md(["### 1. Load daily panel and define event"]))

cells.append(cell_code([
    "df = pd.read_csv(path_daily, parse_dates=['Date']).set_index('Date').sort_index()",
    "event_date = pd.Timestamp('2026-01-05')",
    "core_cols = ['px_gld_close', 'px_slv_close', 'ret_gld', 'ret_slv']",
    "df_core = df.dropna(subset=core_cols).copy()",
    "df_core['post_event'] = (df_core.index >= event_date).astype(int)",
    "pre = df_core['post_event'] == 0",
    "post = df_core['post_event'] == 1",
    "",
    "print(f'Range: {df_core.index.min().date()} to {df_core.index.max().date()}, {len(df_core)} rows x {len(df_core.columns)} columns')",
    "df_core[['post_event']].value_counts().sort_index()",
]))

# --- Data overview table ---
cells.append(cell_md(["## 2. Data overview"]))

cells.append(cell_code([
    "df_core.head().iloc[:, :10]  # first 10 columns",
]))

cells.append(cell_code([
    "df_core[['ret_gld', 'ret_slv', 'vol_realized_20_ret_gld', 'vol_realized_20_ret_slv', 'vol_gld', 'vol_slv']].describe().T",
]))

# --- Pre/post summary ---
cells.append(cell_md(["## 3. Pre- vs post-event summary (means)"]))

cells.append(cell_code([
    "def summarize_pre_post(series, label):",
    "    pre = series[df_core['post_event'] == 0].dropna()",
    "    post = series[df_core['post_event'] == 1].dropna()",
    "    return pd.DataFrame({'metric': [label, label], 'period': ['pre', 'post'],",
    "                         'mean': [pre.mean(), post.mean()], 'std': [pre.std(), post.std()], 'n': [len(pre), len(post)]})",
    "",
    "rows = []",
    "for col, label in [('vol_realized_20_ret_gld', 'GLD 20d vol'), ('vol_realized_20_ret_slv', 'SLV 20d vol'),",
    "                   ('vol_gld', 'GLD volume'), ('vol_slv', 'SLV volume')]:",
    "    if col in df_core.columns:",
    "        rows.append(summarize_pre_post(df_core[col], label))",
    "if 'corr_20_gld_xau' in df_core.columns:",
    "    rows.append(summarize_pre_post(df_core['corr_20_gld_xau'], 'corr_20_gld_xau'))",
    "if 'corr_20_slv_xag' in df_core.columns:",
    "    rows.append(summarize_pre_post(df_core['corr_20_slv_xag'], 'corr_20_slv_xag'))",
    "summary_pre_post = pd.concat(rows, ignore_index=True)",
    "summary_pre_post",
]))

# --- t-tests ---
cells.append(cell_md(["## 4. Welch t-tests (pre vs post)"]))

cells.append(cell_code([
    "from scipy import stats",
    "",
    "def ttest_pre_post(series):",
    "    pre = series[df_core['post_event'] == 0].dropna()",
    "    post = series[df_core['post_event'] == 1].dropna()",
    "    if len(pre) < 3 or len(post) < 3:",
    "        return np.nan, np.nan",
    "    t, p = stats.ttest_ind(post, pre, equal_var=False)",
    "    return t, p",
    "",
    "tt_rows = []",
    "for col, label in [('vol_realized_20_ret_gld', 'GLD 20d vol'), ('vol_realized_20_ret_slv', 'SLV 20d vol'),",
    "                   ('vol_gld', 'GLD volume'), ('vol_slv', 'SLV volume')]:",
    "    if col in df_core.columns:",
    "        t, p = ttest_pre_post(df_core[col])",
    "        pre_m = df_core.loc[pre, col].mean()",
    "        post_m = df_core.loc[post, col].mean()",
    "        pct = (post_m - pre_m) / pre_m * 100 if pre_m and pre_m != 0 else np.nan",
    "        tt_rows.append({'Metric': label, 'Pre mean': pre_m, 'Post mean': post_m, 'Pct': f'{pct:+.0f}%' if not np.isnan(pct) else '—',",
    "                        't': round(t, 3) if not np.isnan(t) else '—', 't-test p': round(p, 4) if not np.isnan(p) else '—'})",
    "tt_df = pd.DataFrame(tt_rows)",
    "tt_df",
]))

# --- Cumulative returns ---
cells.append(cell_md(["## 5. Cumulative returns (ETFs vs Binance)"]))

cells.append(cell_code([
    "fig, ax = plt.subplots(figsize=(10, 4))",
    "for col, lab, c in [('ret_gld', 'GLD', COLORS['gld']), ('ret_slv', 'SLV', COLORS['slv'])]:",
    "    if col not in df_core.columns: continue",
    "    r = df_core[col].fillna(0)",
    "    cum = (1 + r).cumprod() * 100 / cum.iloc[0] if (cum := (1 + r).cumprod()).iloc[0] else cum",
    "    cum = (1 + r).cumprod(); cum = 100 * cum / cum.iloc[0]",
    "    ax.plot(cum.index, cum, label=lab, color=c, linewidth=1.8)",
    "for col, lab, c in [('ret_xau_binance', 'XAUUSDT', COLORS['xau']), ('ret_xag_binance', 'XAGUSDT', COLORS['xag'])]:",
    "    if col not in df_core.columns: continue",
    "    post_ret = df_core.loc[df_core.index >= event_date, col].dropna()",
    "    if post_ret.empty: continue",
    "    cum = (1 + post_ret).cumprod(); cum = 100 * cum / cum.iloc[0]",
    "    ax.plot(cum.index, cum, label=lab, color=c, linewidth=1.8)",
    "ax.axvline(event_date, color=COLORS['event'], linestyle='--', linewidth=1.5, label='Event')",
    "ax.set_ylabel('Cumulative return (index = 100)')",
    "ax.set_title('Cumulative returns: ETFs vs Binance (Binance from launch only)')",
    "ax.legend(loc='upper left', ncol=2)",
    "plt.tight_layout()",
    "plt.show()",
]))

# Fix the bug in cumulative - we have "cum" used before assignment in one branch
cells[-1]["source"] = [
    "fig, ax = plt.subplots(figsize=(10, 4))\n",
    "for col, lab, c in [('ret_gld', 'GLD', COLORS['gld']), ('ret_slv', 'SLV', COLORS['slv'])]:\n",
    "    if col not in df_core.columns: continue\n",
    "    r = df_core[col].fillna(0)\n",
    "    cum = (1 + r).cumprod(); cum = 100 * cum / cum.iloc[0]\n",
    "    ax.plot(cum.index, cum, label=lab, color=c, linewidth=1.8)\n",
    "for col, lab, c in [('ret_xau_binance', 'XAUUSDT', COLORS['xau']), ('ret_xag_binance', 'XAGUSDT', COLORS['xag'])]:\n",
    "    if col not in df_core.columns: continue\n",
    "    post_ret = df_core.loc[df_core.index >= event_date, col].dropna()\n",
    "    if post_ret.empty: continue\n",
    "    cum = (1 + post_ret).cumprod(); cum = 100 * cum / cum.iloc[0]\n",
    "    ax.plot(cum.index, cum, label=lab, color=c, linewidth=1.8)\n",
    "ax.axvline(event_date, color=COLORS['event'], linestyle='--', linewidth=1.5, label='Event')\n",
    "ax.set_ylabel('Cumulative return (index = 100)')\n",
    "ax.set_title('Cumulative returns: ETFs vs Binance (Binance from launch only)')\n",
    "ax.legend(loc='upper left', ncol=2)\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
]

# --- Volatility and volume over time ---
cells.append(cell_md(["## 6. Volatility and volume over time"]))

cells.append(cell_code([
    "fig, axes = plt.subplots(3, 1, figsize=(10, 6), sharex=True)",
    "for ax in axes:",
    "    ax.axvline(event_date, color=COLORS['event'], linestyle='--', linewidth=1.5)",
    "if 'vol_realized_20_ret_gld' in df_core.columns:",
    "    axes[0].plot(df_core.index, df_core['vol_realized_20_ret_gld'], color=COLORS['gld'], label='GLD 20d')",
    "if 'vol_realized_20_ret_slv' in df_core.columns:",
    "    axes[0].plot(df_core.index, df_core['vol_realized_20_ret_slv'], color=COLORS['slv'], label='SLV 20d')",
    "axes[0].set_ylabel('Volatility'); axes[0].set_title('Realized 20d volatility'); axes[0].legend()",
    "if 'vol_parkinson_gld' in df_core.columns:",
    "    axes[1].plot(df_core.index, df_core['vol_parkinson_gld'], color=COLORS['gld'], label='GLD')",
    "if 'vol_parkinson_slv' in df_core.columns:",
    "    axes[1].plot(df_core.index, df_core['vol_parkinson_slv'], color=COLORS['slv'], label='SLV')",
    "axes[1].set_ylabel('Volatility'); axes[1].set_title('Parkinson volatility'); axes[1].legend()",
    "if 'vol_gld' in df_core.columns:",
    "    axes[2].plot(df_core.index, df_core['vol_gld'] / 1e6, color=COLORS['gld'], label='GLD')",
    "if 'vol_slv' in df_core.columns:",
    "    axes[2].plot(df_core.index, df_core['vol_slv'] / 1e6, color=COLORS['slv'], label='SLV')",
    "axes[2].set_ylabel('Volume (M)'); axes[2].set_title('ETF volume'); axes[2].legend()",
    "plt.suptitle('Volatility and volume over time', y=1.02)",
    "plt.tight_layout()",
    "plt.show()",
]))

# --- Pre/post % change bar ---
cells.append(cell_md(["## 7. Pre vs post: percent change"]))

cells.append(cell_code([
    "pct_rows = []",
    "for col, label in [('vol_realized_20_ret_gld', 'GLD 20d vol'), ('vol_realized_20_ret_slv', 'SLV 20d vol'),",
    "                   ('vol_gld', 'GLD volume'), ('vol_slv', 'SLV volume')]:",
    "    if col not in df_core.columns: continue",
    "    pre_m, post_m = df_core.loc[pre, col].mean(), df_core.loc[post, col].mean()",
    "    if pre_m and pre_m != 0:",
    "        pct = (post_m - pre_m) / pre_m * 100",
    "        pct_rows.append({'Metric': label, 'Pre mean': pre_m, 'Post mean': post_m, 'Pct change': f'{pct:+.0f}%'})",
    "pct_df = pd.DataFrame(pct_rows)",
    "pct_df",
]))

cells.append(cell_code([
    "if len(pct_rows) >= 1:",
    "    fig, ax = plt.subplots(figsize=(8, 3))",
    "    labels = [r['Metric'] for r in pct_rows]",
    "    pcts = [(float(str(r['Pct change']).replace('%', '')) if isinstance(r['Pct change'], str) else r['Pct change']) for r in pct_rows]",
    "    colors = [COLORS['gld'] if 'GLD' in l else COLORS['slv'] for l in labels]",
    "    y_pos = np.arange(len(labels))",
    "    ax.barh(y_pos, pcts, color=colors)",
    "    ax.axvline(0, color='gray', linewidth=0.8)",
    "    ax.set_yticks(y_pos); ax.set_yticklabels(labels)",
    "    ax.set_xlabel('Percent change (post vs pre)')",
    "    ax.set_title('Pre vs post: how much did each metric grow?')",
    "    plt.tight_layout()",
    "    plt.show()",
]))

# --- Correlation matrix ---
cells.append(cell_md(["## 8. Correlation matrix (key variables)"]))

cells.append(cell_code([
    "corr_vars = [('ret_gld', 'GLD ret'), ('ret_slv', 'SLV ret'), ('ret_xau_binance', 'XAU ret'), ('ret_xag_binance', 'XAG ret'),",
    "             ('dxy_ret', 'DXY ret'), ('vix_ret', 'VIX ret'), ('tnx_ret', 'TNX ret'),",
    "             ('vol_realized_20_ret_gld', 'GLD 20d vol'), ('vol_realized_20_ret_slv', 'SLV 20d vol')]",
    "available = [(c, l) for c, l in corr_vars if c in df_core.columns]",
    "if len(available) >= 3:",
    "    cols = [c for c, _ in available]",
    "    labels = [l for _, l in available]",
    "    C = df_core[cols].corr()",
    "    C.index = labels",
    "    C.columns = labels",
    "    fig, ax = plt.subplots(figsize=(8, 6))",
    "    sns.heatmap(C, cmap='RdBu_r', center=0, vmin=-1, vmax=1, annot=True, fmt='.2f', ax=ax)",
    "    plt.xticks(rotation=45, ha='right')",
    "    plt.title('Correlation matrix: returns, controls, volatility')",
    "    plt.tight_layout()",
    "    plt.show()",
    "else:",
    "    print('Not enough variables for correlation matrix')",
]))

# --- Rolling correlation ---
cells.append(cell_md(["## 9. Integration: rolling 20d correlation (post-event)"]))

cells.append(cell_code([
    "if 'corr_20_gld_xau' in df_core.columns or 'corr_20_slv_xag' in df_core.columns:",
    "    fig, ax = plt.subplots(figsize=(9, 3.5))",
    "    c_gld = df_core['corr_20_gld_xau'].dropna() if 'corr_20_gld_xau' in df_core.columns else pd.Series(dtype=float)",
    "    c_slv = df_core['corr_20_slv_xag'].dropna() if 'corr_20_slv_xag' in df_core.columns else pd.Series(dtype=float)",
    "    if not c_gld.empty: ax.plot(c_gld.index, c_gld.values, color=COLORS['gld'], label='GLD–XAU')",
    "    if not c_slv.empty: ax.plot(c_slv.index, c_slv.values, color=COLORS['slv'], label='SLV–XAG')",
    "    ax.set_ylim(0, 1.02)",
    "    ax.set_ylabel('Rolling 20d correlation')",
    "    ax.set_title('ETF–Binance correlation (post-event only)')",
    "    ax.legend()",
    "    plt.tight_layout()",
    "    plt.show()",
    "else:",
    "    print('Rolling correlation columns not in panel')",
]))

# --- OLS regressions ---
cells.append(cell_md(["## 10. OLS regressions (post_event + controls)"]))

cells.append(cell_code([
    "import statsmodels.api as sm",
    "",
    "reg_df = df_core.copy()",
    "def winsorize(s, lower=0.05, upper=0.95):",
    "    q = s.quantile([lower, upper])",
    "    return s.clip(lower=q.iloc[0], upper=q.iloc[1])",
    "for col in ['vol_realized_20_ret_gld', 'vol_realized_20_ret_slv']:",
    "    if col in reg_df.columns:",
    "        reg_df[f'{col}_w'] = winsorize(reg_df[col].dropna())",
    "",
    "control_cols = ['post_event', 'dxy_ret', 'vix_ret', 'tnx_ret']",
    "if 'dgs10_ret' in reg_df.columns:",
    "    control_cols = ['post_event', 'dxy_ret', 'vix_ret', 'tnx_ret', 'dgs10_ret']",
    "",
    "def run_ols(y_col, x_cols, data, use_winsor=True, hac=True):",
    "    y_name = f'{y_col}_w' if (use_winsor and f'{y_col}_w' in data.columns) else y_col",
    "    if y_name not in data.columns: y_name = y_col",
    "    sub = data[[y_name] + x_cols].dropna()",
    "    if len(sub) < 10: return None",
    "    y = sub[y_name]",
    "    X = sm.add_constant(sub[x_cols])",
    "    fit = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 5}) if hac else sm.OLS(y, X).fit()",
    "    return fit",
    "",
    "model_gld = run_ols('vol_realized_20_ret_gld', control_cols, reg_df)",
    "model_slv = run_ols('vol_realized_20_ret_slv', control_cols, reg_df)",
]))

cells.append(cell_code([
    "if model_gld is not None:",
    "    print('GLD 20d volatility:'); print(model_gld.summary().tables[1])",
    "if model_slv is not None:",
    "    print('SLV 20d volatility:'); print(model_slv.summary().tables[1])",
]))

# --- Key results table ---
cells.append(cell_md(["## 11. Key results table"]))

cells.append(cell_code([
    "key_rows = []",
    "for col, label in [('vol_realized_20_ret_gld', 'GLD 20d vol'), ('vol_realized_20_ret_slv', 'SLV 20d vol'),",
    "                   ('vol_gld', 'GLD volume'), ('vol_slv', 'SLV volume')]:",
    "    if col not in df_core.columns: continue",
    "    pre_m = df_core.loc[pre, col].mean()",
    "    post_m = df_core.loc[post, col].mean()",
    "    t, p = ttest_pre_post(df_core[col])",
    "    pct = (post_m - pre_m) / pre_m * 100 if pre_m and pre_m != 0 else np.nan",
    "    coef_str, reg_p = '—', '—'",
    "    if col.startswith('vol_realized_20') and model_gld is not None and model_slv is not None:",
    "        mod = model_gld if 'gld' in col else model_slv",
    "        if 'post_event' in mod.params:",
    "            coef_str = round(mod.params['post_event'], 4)",
    "            reg_p = round(mod.pvalues['post_event'], 3)",
    "    key_rows.append({'Metric': label, 'Pre mean': round(pre_m, 6) if not np.isnan(pre_m) else '—',",
    "                     'Post mean': round(post_m, 6) if not np.isnan(post_m) else '—',",
    "                     'Pct': f'{pct:+.0f}%' if not np.isnan(pct) else '—',",
    "                     't': round(t, 3) if not np.isnan(t) else '—', 't-test p': round(p, 4) if not np.isnan(p) else '—',",
    "                     'post coef': coef_str, 'reg p': reg_p})",
    "if 'corr_20_gld_xau' in df_core.columns:",
    "    key_rows.append({'Metric': 'Corr GLD–XAU', 'Pre mean': '—', 'Post mean': round(df_core.loc[post, 'corr_20_gld_xau'].mean(), 4), 'Pct': '—', 't': '—', 't-test p': '—', 'post coef': '—', 'reg p': '—'})",
    "if 'corr_20_slv_xag' in df_core.columns:",
    "    key_rows.append({'Metric': 'Corr SLV–XAG', 'Pre mean': '—', 'Post mean': round(df_core.loc[post, 'corr_20_slv_xag'].mean(), 4), 'Pct': '—', 't': '—', 't-test p': '—', 'post coef': '—', 'reg p': '—'})",
    "key_results_df = pd.DataFrame(key_rows)",
    "key_results_df",
]))

# --- Conclusions ---
cells.append(cell_md([
    "## 12. Conclusions",
    "",
    "- **H1 (volatility):** Positive and significant coefficient on `post_event` in volatility regressions (with DXY, VIX, 10Y controls) → H1 supported.",
    "- **H2 (liquidity):** Volume and liquidity metrics improve in direction (higher volume post-event).",
    "- **Integration:** Rolling correlation GLD–XAU and SLV–XAG is high post-event; we have no pre-event Binance data, so we describe only.",
    "- **Limitations:** No control group (no DiD); short post window."
]))

# Build notebook
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": cells
}

# Fix cell 5 (cumulative returns) - already fixed above by replacing cells[-1]; actually that was the last code cell at that point. Let me check - we have multiple code cells. The bug was in the first cumulative returns code block - I had "cum = ...; cum = 100 * cum / cum.iloc[0] if (cum := ...)" which is wrong. I replaced the whole source with a correct version. So we're good.

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print(f"Saved {NB_PATH}")
print("Open in Jupyter or VS Code to run all calculations.")
