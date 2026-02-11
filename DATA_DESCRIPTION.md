## Опис даних / Data description

Нижче описано всі основні набори даних у `data/raw/`, їх джерела, періоди та основні змінні.  
The table below describes all main datasets in `data/raw/`, their sources, periods and key variables.

---

### 1. Binance gold & silver futures (1‑minute klines)

- **Файли / Files**:  
  - `binance_xauusdt_1m.csv`  
  - `binance_xagusdt_1m.csv`  
  - `binance_gold_silver_1m_all.csv` (об’єднаний / combined)
- **Джерело / Source**: Binance USDT‑margined Futures API  
  - Endpoint: `GET /fapi/v1/continuousKlines`  
  - Docs: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Continuous-Contract-Kline-Candlestick-Data`
- **Параметри запиту / Request params** (основні):
  - `pair = "XAUUSDT"` або `pair = "XAGUSDT"`  
  - `contractType = "TRADIFI_PERPETUAL"`  
  - `interval = "1m"`  
  - `startTime` ≈ 2026‑01‑05 (launch) for XAUUSDT, 2026‑01‑07 for XAGUSDT  
  - `endTime` = now
- **Приблизні розміри / Approx sizes**:
  - `binance_xauusdt_1m.csv`: ~53 800 рядків / rows  
  - `binance_xagusdt_1m.csv`: ~50 400 рядків / rows  
  - Сумарно / total: 100k+ спостережень / observations
- **Основні змінні / Key columns**:
  - `open_time`, `close_time` – час відкриття/закриття хвилинної свічки (UTC)  
  - `open`, `high`, `low`, `close` – ціни  
  - `volume` – обсяг в базовому активі  
  - `quote_volume` – обсяг у котирувальній валюті (USDT)  
  - `num_trades` – кількість угод  
  - `taker_buy_volume`, `taker_buy_quote_volume` – агресивні покупки  
  - `pair`, `interval`, `contract_type` – метадані
- **Перевірка коректності / Sanity checks**:
  - Перші дати збігаються з анонсованими датами запуску контракта (2026‑01‑05 для XAUUSDT, 2026‑01‑07 для XAGUSDT).  
  - Ціни та обсяги мають правдоподібні діапазони (gold ~ 4 300–5 000, silver ~ 80 USD).  
  - Немає порожніх файлів; усі обов’язкові стовпчики присутні.

---

### 2. Binance funding rate & open interest

- **Файли / Files**:
  - `binance_xauusdt_funding.csv`  
  - `binance_xagusdt_funding.csv`  
  - `binance_xauusdt_open_interest.csv`  
  - `binance_xagusdt_open_interest.csv`
- **Джерело / Source**: Binance Futures API  
  - Funding history: `GET /fapi/v1/fundingRate?symbol=XAUUSDT` (або XAGUSDT)  
  - Open interest: `GET /fapi/v1/openInterest?symbol=XAUUSDT` (або XAGUSDT)
- **Основні змінні / Key columns**:
  - Funding:
    - `fundingTime` – час нарахування (UTC)  
    - `fundingRate` – ставка фінансування  
    - `markPrice` – mark price
  - Open interest:
    - `time` – час зняття показника (UTC)  
    - `openInterest` – кількість відкритих контрактів
- **Перевірка / Checks**:
  - `fundingTime` у 2026‑01+ (після запуску контрактів).  
  - Для XAUUSDT funding зараз може бути близьким до 0, що типово для нових інструментів.  
  - `openInterest` додатний, без очевидних аномалій.

---

### 3. ETFs: GLD, IAU, SLV, GDX, SIL (daily)

- **Файл / File**:  
  - `etf_gld_iau_slv_gdx_sil_daily.csv`
- **Джерело / Source**: Yahoo Finance via `yfinance`  
  - Docs: `https://github.com/ranaroussi/yfinance`
- **Параметри / Parameters**:
  - Tickers: `["GLD", "IAU", "SLV", "GDX", "SIL"]`  
  - Period: from `2025-09-01` to ~`2026-02-11`  
  - Frequency: 1 day (`interval="1d"`)
- **Структура / Structure**:
  - Multi-index columns: рівень 1 — `Ticker` (`IAU`, `SLV`, `SIL`, `GDX`, `GLD`),  
    рівень 2 — `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`.  
  - Index: `Date`.
- **Перевірка / Checks**:
  - ~100+ торгових днів для кожного ETF.  
  - Ціни в діапазонах, узгоджених із ринковими: GLD ~ 320–340, SLV ~ 36–38 тощо.  
  - Відсутні порожні дні в межах торгового календаря (окрім вихідних/свят).

---

### 4. Control variables: DXY, VIX, 10Y yield (daily)

- **Файл / File**:  
  - `controls_dxy_vix_tnx_daily.csv`
- **Джерело / Source**: Yahoo Finance via `yfinance`
- **Tickers**:
  - DXY (U.S. Dollar Index): `DX-Y.NYB`  
  - VIX (CBOE Volatility Index): `^VIX`  
  - 10‑year Treasury yield proxy: `^TNX`
- **Період / Period**:
  - from `2025-09-01` to ~`2026-02-11`, 1‑day frequency.
- **Структура / Structure**:
  - Multi-index columns: ticker on level 1, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume` on level 2.  
  - Index: `Date`.
- **Перевірка / Checks**:
  - DXY ~ 97–99; VIX ~ 15–20; `^TNX` ~ 4.0–4.3 — діапазони відповідають ринку.  
  - Немає порожніх файлів; дані повністю корелюють із періодом ETF.

---

### 5. Потенційні наступні кроки / Next steps

- **UA**:  
  - На основі цих сирих даних можна побудувати “аналітичний” датасет із:  
    доходностями, волатильностями (rolling std, Parkinson, Garman–Klass),  
    rolling кореляціями/бетами між Binance та ETF, індикаторами подій (`post_event`, `event_window_7`, `event_window_14`),  
    проксі ліквідності (обсяг, Amihud), та контрольними змінними (DXY, VIX, TNX).  
  - Це дозволить легко виконати вимогу курсу щодо 10 000+ спостережень і 50+ змінних.

- **EN**:  
  - Based on these raw datasets you can build an “analytics” table with:  
    returns, volatility measures (rolling std, Parkinson, Garman–Klass),  
    rolling correlations/betas between Binance and ETFs, event indicators (`post_event`, `event_window_7`, `event_window_14`),  
    liquidity proxies (volume, Amihud), and control variables (DXY, VIX, TNX).  
  - This will easily satisfy the course requirement of 10,000+ observations and 50+ variables.

