## Перелік та ідея змінних / List and rationale of variables

Нижче — плановий набір змінних, який буде побудовано в аналітичному датасеті (напр. `data/processed/panel_daily.csv`).  
Together these features give 87 variables in the daily panel.

---

### 1. Цінові ряди та доходності / Price series and returns

**Binance TRADIFI futures (XAUUSDT, XAGUSDT)** — агреговані до daily:
- `px_xau_binance_close`, `px_xag_binance_close` – daily close prices.
- `ret_xau_binance`, `ret_xag_binance` – log returns: \(\ln(P_t) - \ln(P_{t-1})\).
- `ret_abs_xau_binance`, `ret_abs_xag_binance` – absolute returns.
- `ret_sq_xau_binance`, `ret_sq_xag_binance` – squared returns.

**ETFs (GLD, IAU, SLV, GDX, SIL)**:
- `px_gld_close`, `px_iau_close`, `px_slv_close`, `px_gdx_close`, `px_sil_close` – daily close prices.
- `ret_gld`, `ret_iau`, `ret_slv`, `ret_gdx`, `ret_sil` – log returns.
- `ret_abs_gld`, `ret_abs_slv` – absolute returns (основні метали / main metals).

_≈ 4 (Binance) + 5 (ETF returns) + 2 (abs ETF) + 2 (abs Binance) + 2 (sq Binance) ≈ 15+ змінних._

---

### 2. Волатильність / Volatility measures

Розраховуються окремо для Binance та ETF (на daily даних):

- `vol_realized_10_xau_binance`, `vol_realized_10_xag_binance` – 10‑day rolling std of returns.  
- `vol_realized_20_xau_binance`, `vol_realized_20_xag_binance` – 20‑day rolling std.
- `vol_realized_10_gld`, `vol_realized_10_slv` – 10‑day rolling std for ETF GLD, SLV.  
- `vol_realized_20_gld`, `vol_realized_20_slv` – 20‑day rolling std.

High–low based volatility:
- `vol_parkinson_gld`, `vol_parkinson_slv` – Parkinson volatility for ETFs (GLD, SLV).  
- `vol_parkinson_xau_binance`, `vol_parkinson_xag_binance` – for Binance series.
- `vol_gk_gld`, `vol_gk_slv` – Garman–Klass volatility for ETFs.  
- `vol_gk_xau_binance`, `vol_gk_xag_binance` – for Binance.

_Разом ~16 волатильнісних змінних._

---

### 3. Зв’язок Binance–ETF / Binance–ETF integration

- `corr_20_gld_xau` – 20‑day rolling correlation between `ret_gld` and `ret_xau_binance`.  
- `corr_20_slv_xag` – аналогічно для срібла / silver.
- `beta_60_gld_on_xau` – rolling 60‑day beta of GLD returns on Binance XAUUSDT returns.  
- `beta_60_slv_on_xag` – аналогічно для SLV/XAGUSDT.
- `vol_ratio_gld_xau` – `vol_realized_20_gld / vol_realized_20_xau_binance`.  
- `vol_ratio_slv_xag` – аналогічно для срібла.  
- `abs_return_gap_gld_xau` – `|ret_gld| - |ret_xau_binance|`.  
- `abs_return_gap_slv_xag` – аналогічно для срібла.

_Ще 8+ змінних, які безпосередньо ловлять “інтеграцію” ринків._

---

### 4. Event‑dummies / подієві змінні

Базуємося на даті запуску контрактів:
- `post_event` – 1 після дати запуску (наприклад, 2026‑01‑05), 0 до.  
- `event_window_7` – 1 для перших 7 днів після події, 0 інакше.  
- `event_window_14` – 1 для перших 14 днів після події, 0 інакше.

_Ще 3 змінні, зручні для event‑study аналізу._

---

### 5. Ліквідність та поведінка торгівлі / Liquidity and trading behavior

**ETFs:**
- `vol_gld`, `vol_slv` – daily trading volume.  
- `log_vol_gld`, `log_vol_slv` – log(volume).  
- `amihud_gld`, `amihud_slv` – Amihud illiquidity: \(|ret| / volume\).  
- `amihud_20_gld`, `amihud_20_slv` – 20‑day rolling average of Amihud.

**Binance futures:**
- `vol_xau_binance`, `vol_xag_binance` – aggregated daily volume from 1m data.  
- `log_vol_xau_binance`, `log_vol_xag_binance` – logarithms of volumes.  
- `trades_xau_binance`, `trades_xag_binance` – aggregated daily `num_trades`.  
- `log_trades_xau_binance`, `log_trades_xag_binance` – логарифми кількості угод.

_Ще 12+ змінних, що відображають ліквідність._

---

### 6. Funding, open interest та позиціонування / Funding, open interest and positioning

На базі `binance_*_funding.csv` та `binance_*_open_interest.csv`, агреговано на daily:

- `funding_xau`, `funding_xag` – daily funding rate (можливо 0 на початку).  
- `funding_change_xau`, `funding_change_xag` – first difference of funding.  
- `funding_extreme_xau`, `funding_extreme_xag` – dummy = 1, якщо funding в upper 5% historical quantile (proxy for speculative pressure).

- `oi_xau`, `oi_xag` – open interest (можливо на окремі дні; можна forward‑fill).  
- `oi_xau_change`, `oi_xag_change` – day‑to‑day changes.

**Чому бувають NaN / Why NaNs:**  
- **OI change:** Binance Open Interest API часто повертає один снапшот (одна дата). У панелі тоді лише один день має `oi_*`; для решти днів значення відсутнє, тому `diff()` дає NaN. Потрібна історична серія OI по днях, щоб мати ненульові зміни.  
- **Funding extreme:** Якщо funding rate відсутній (напр. до лістингу), тепер заповнюється 0 (не extreme). Раніше порівняння з quantile давало NaN.

_Ще ~8 змінних, які відбивають плечі та спекулятивну активність._

---

### 7. Контрольні змінні / Control variables

На базі Yahoo `controls_dxy_vix_tnx_daily.csv` та FRED (якщо завантажено):

- Levels:  
  - `dxy`, `vix`, `tnx` – closing levels of DXY, VIX, 10Y yield (Yahoo ^TNX).  
  - `dgs10` – 10-Year Treasury Constant Maturity Rate (FRED DGS10), якщо файл `fred_dgs10_daily.csv` є.  
- Changes / returns:  
  - `dxy_ret`, `vix_ret`, `tnx_ret` – log returns/changes для Yahoo контролів.  
  - `dgs10_ret` – log return для DGS10 (FRED), якщо присутній.

_6 змінних (Yahoo) + до 2 (FRED dgs10, dgs10_ret)._

---

### 8. Підсумок / Summary

Якщо підсумувати орієнтовно:

- Блок 1 (returns, prices): ~15+  
- Блок 2 (volatility): ~16  
- Блок 3 (integration): ~8  
- Блок 4 (event dummies): 3  
- Блок 5 (liquidity): ~12  
- Блок 6 (funding & OI): ~8  
- Блок 7 (controls): 6–8 (Yahoo + опційно FRED DGS10)  

Разом легко **>60 змінних** у фінальному датасеті, навіть якщо частину потім відкинемо у регресіях.

У наступному кроці можна створити ноутбук (наприклад, `analysis.ipynb`), який:
- завантажує сирі CSV із `data/raw/`,  
- конструює наведені вище змінні,  
- зберігає підсумковий `panel_daily.csv` або `features_daily.csv` разом із цим описом.

