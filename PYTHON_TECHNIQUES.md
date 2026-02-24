# Python analytical techniques used in this project

This document lists **Python techniques and libraries** used in the project, aligned with the course (References examples) and showcasing analytical capabilities of the language.

---

## 1. Data handling (pandas)

| Technique | Where we use it | Class example |
|-----------|-----------------|----------------|
| **pd.read_csv**, **parse_dates**, **set_index** | Loading `features_daily.csv`, index as datetime | Gas Stations, Debt vs Renew |
| **merge / join** | Joining ETF, controls, FRED, Binance by date; 1m panel merged with daily by date | Debt vs Renew: `pd.merge(..., on='Country', how='inner')` |
| **groupby + mean/agg** | Event-time dynamics: `df_et.groupby("week_rel")["vol_realized_20_ret_gld"].mean()` | — |
| **rolling + corr/std** | Rolling correlation, rolling std (volatility), rolling beta | — |
| **dropna**, **fillna**, **clip** | Cleaning and winsorization | Debt: `dropna(subset=[...])` |
| **sort_values**, **sort_index** | Ordering by date or by value | Debt: `sort_values(by='Wind', ascending=False).head(10)` |
| **.apply(function)** | Custom winsorize, or element-wise transform | Debt: `df['Country'].apply(clean_country_name)` |
| **.loc**, **.iloc**, boolean indexing | Pre/post split: `df_core.loc[post, col]`, filtering by date | — |
| **melt** | Reshaping for boxplots (Metric, Period, Value) | — |

---

## 2. Numerical and statistics (numpy, scipy, statsmodels)

| Technique | Where we use it | Class example |
|-----------|-----------------|----------------|
| **numpy.log**, **diff** | Log returns, growth rates | — |
| **np.polyfit / np.poly1d** | Regression line in scatter (GLD vs XAU returns) | — |
| **scipy.stats.ttest_ind** | Welch t-test (pre vs post), `equal_var=False` | — |
| **scipy.stats.levene** | Test for equality of variances (validation) | — |
| **statsmodels.OLS** | Linear regression (post_event + controls), HAC SE | Gas Stations: `sm.OLS`; proj4: regression |
| **statsmodels ts (optional)** | ACF plot or AutoReg for time series (see below) | proj4: `AutoReg`, `VAR` |

---

## 3. Visualization (matplotlib, seaborn, plotly)

| Technique | Where we use it | Class example |
|-----------|-----------------|----------------|
| **matplotlib: subplots, plot, axvline, axvspan** | Time series, event line, cumulative returns | — |
| **seaborn: heatmap, boxplot** | Correlogram, pre/post boxplots | Gas: seaborn, matplotlib |
| **Plotly (optional)** | Interactive time series or scatter with hover | Debt vs Renew: `px.choropleth`, `px.scatter` |

---

## 4. APIs and I/O (requests, yfinance)

| Technique | Where we use it | Class example |
|-----------|-----------------|----------------|
| **requests.get**, **params**, **.json()** | Binance API, FRED API in `download_data.py` | — |
| **yfinance.download** | ETF and controls (daily and 1m) | — |
| **os.path**, **os.getenv** | Paths, FRED_API_KEY | — |

---

## 5. Code structure (Python language)

| Technique | Where we use it | Class example |
|-----------|-----------------|----------------|
| **Functions (def)** | `run_ols`, `ttest_pre_post`, `summarize_pre_post`, `winsorize`, `fmt_val` | Debt: `clean_country_name`, `clean_number` |
| **List/dict comprehensions** | `[c for c in df_core.columns if ...]`, `{col: label for ...}` | — |
| **Type hints (optional)** | `def run_ols(y_col: str, x_cols: list, ...)` in analysis | — |
| **f-strings** | Formatted output, plot labels | — |
| **argparse** | `download_data.py --refresh` | — |

---

## 6. Techniques from class we added for consistency

- **Plotly**: one interactive chart (e.g. cumulative returns or volatility) so the report uses the same library as Debt vs Renew.
- **statsmodels.tsa**: ACF plot or simple AutoReg for one return series to show time-series analytics as in proj4.
- **.apply()**: used in winsorization or in a small helper to keep code readable.

See the "Python techniques" section in `analysis.qmd` for the actual code (Plotly figure and ACF / AutoReg block).
