# Перевірка наявності даних: Binance gold/silver perpetual vs ETF

## Висновок: **Дані є, проєкт реалізуємо**

Усі потрібні джерела перевірені; обмеження лише по довжині історії (контракти з січня 2026).

---

## 1. Binance (XAUUSDT, XAGUSDT)

### Контракти та дати запуску
- **XAUUSDT**: запуск **5 січня 2026**
- **XAGUSDT**: запуск **7 січня 2026**
- Тип: **TRADIFI_PERPETUAL** (не звичайний `PERPETUAL`). У запитах **обов’язково** вказувати `contractType=TRADIFI_PERPETUAL`.

### Що перевірено і працює

| Що потрібно | Endpoint / спосіб | Статус |
|-------------|-------------------|--------|
| OHLCV, number of trades, taker buy volume | `GET /fapi/v1/continuousKlines` з `pair=XAUUSDT` або `XAGUSDT`, `contractType=TRADIFI_PERPETUAL`, `interval=1d` (або 1h, 15m) | ✅ Є |
| Funding rate | `GET /fapi/v1/fundingRate?symbol=XAUUSDT` (так само XAGUSDT) | ✅ Є |
| Open interest (поточна) | `GET /fapi/v1/openInterest?symbol=XAUUSDT` | ✅ Є |

**Обмеження:**
- Історія лише з моменту запуску (січень 2026), тобто **pre‑event** буде коротким (кілька тижнів до 5/7 січня), якщо брати тільки Binance.
- Для **pre‑event** можна використати: (1) дані ETF/спот за листопад–грудень 2025 як “до події”, (2) чітко описати в роботі коротке pre‑вікно для Binance і зробити robustness на 30/30 та 90/90 днів для ETF.

### Приклад запиту (klines)
```
GET https://fapi.binance.com/fapi/v1/continuousKlines?pair=XAUUSDT&contractType=TRADIFI_PERPETUAL&interval=1d&limit=150
```
Відповідь: масив свічок [open time, open, high, low, close, volume, close time, quote volume, number of trades, taker buy volume, taker buy quote volume, ignore].

---

## 2. ETF (Yahoo Finance)

| Тикер | Опис | Статус |
|-------|------|--------|
| GLD | Gold | ✅ |
| IAU | Gold (менший) | ✅ |
| SLV | Silver | ✅ |
| GDX, SIL | Майнери (опційно) | ✅ |

Завантаження через **yfinance**: `yf.download(["GLD","IAU","SLV"], start="2025-09-01", end="2026-02-11")` — перевірено, дані є (наприклад, 68+ днів для періоду 2025-11 — 2026-02).

---

## 3. Контрольні змінні

| Змінна | Джерело | Тикер / серія | Статус |
|--------|---------|----------------|--------|
| DXY | Yahoo Finance | `DX-Y.NYB` | ✅ |
| VIX | Yahoo Finance | `^VIX` | ✅ |
| US 10Y yield | Yahoo Finance | `^TNX` | ✅ |
| Fed Funds / інші ставки | FRED | fredapi (потрібен API key) | Опційно |

Для мінімальної реалізації курсу **DXY, VIX, 10Y через yfinance достатньо**.

---

## 4. Рекомендації під ваш дизайн

1. **Event dates**: використовувати **5 січня 2026** (XAUUSDT) та **7 січня 2026** (XAGUSDT); у звіті можна взяти одну “подію” (наприклад, 5 січня) або окремо золото/срібло.
2. **Pre‑вікно**: для ETF — 60 trading days до події (листопад–грудень 2025); для Binance — максимум що є до 5/7 січня (декілька днів). Це чесно описати як limitation і підкріпити висновки переважно ETF‑стороною та rolling corr/beta після запуску.
3. **Частота**: Binance — 1h або 1d (1d для зіставності з ETF); ETF — 1d.
4. **Код**: у всіх запитах до Binance вказувати **contractType=TRADIFI_PERPETUAL**; звичайний `PERPETUAL` для XAUUSDT/XAGUSDT повертає помилку.

---

## 5. Файли в репо

- `check_data_availability.py` — скрипт перевірки (ETF, Binance klines/funding/OI, контрольні змінні). Запуск: `python3 check_data_availability.py`.
- Цей звіт: `DATA_AVAILABILITY_REPORT.md`.

Далі можна робити каркас ноутбука Colab: завантаження (Binance + yfinance), чистка, feature engineering, графіки, базові регресії та event‑study таблиці.
