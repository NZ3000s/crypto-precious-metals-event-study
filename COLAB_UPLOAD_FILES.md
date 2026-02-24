# Які файли завантажити в Colab

Щоб запускати ноутбук у Google Colab без викликів Binance API (і без помилки 451), завантаж дані локально, потім підгрузи ці файли в Colab.

## Варіант 1: Тільки зведені панелі (найпростіше)

Завантаж **лише ці файли** в папку `data/processed/` у Colab:

| Файл | Призначення |
|------|-------------|
| **features_daily.csv** | Основний щоденний датасет для event study (обовʼязково) |
| features_hourly.csv | Годинна панель (опційно) |
| features_1m.csv | Хвилинна панель для розрахунків по 1m (опційно) |

**Як:** у Colab створи папку `data/processed/`, завантаж туди принаймні `features_daily.csv`. У ноутбуку потрібно буде **пропустити** комірки завантаження з API та побудови панелей і почати з комірки, що читає `features_daily.csv`.

---

## Варіант 2: Сирі дані (щоб у Colab збирати панелі самому)

Завантаж файли в папку `data/raw/` у Colab. Після цього можна запускати також `build_features` у Colab (якщо є файл `build_features.py`).

### Обовʼязкові (без них панель не зібрати):

| Файл | Опис |
|------|------|
| **etf_gld_iau_slv_gdx_sil_daily.csv** | ETF (GLD, IAU, SLV, GDX, SIL) щоденно |
| **controls_dxy_vix_tnx_daily.csv** | Контролі DXY, VIX, TNX щоденно |
| **binance_xauusdt_1m.csv** | Binance XAUUSDT 1m klines |
| **binance_xagusdt_1m.csv** | Binance XAGUSDT 1m klines |

### Додаткові (funding / open interest):

| Файл | Опис |
|------|------|
| binance_xauusdt_funding.csv | Funding rate XAUUSDT |
| binance_xagusdt_funding.csv | Funding rate XAGUSDT |
| binance_xauusdt_open_interest.csv | Open interest XAUUSDT |
| binance_xagusdt_open_interest.csv | Open interest XAGUSDT |

### Опційно:

| Файл | Опис |
|------|------|
| fred_dgs10_daily.csv | DGS10 (10Y Treasury), якщо є |
| etf_gld_slv_1m_last7d.csv | GLD/SLV 1m за останні 7 днів |

---

## Структура папок у Colab

```
/content/   (або де у тебе ноутбук)
├── research.ipynb
├── build_features.py          # потрібен для варіанту 2
├── data/
│   ├── raw/
│   │   ├── etf_gld_iau_slv_gdx_sil_daily.csv
│   │   ├── controls_dxy_vix_tnx_daily.csv
│   │   ├── binance_xauusdt_1m.csv
│   │   ├── binance_xagusdt_1m.csv
│   │   └── ...
│   └── processed/
│       ├── features_daily.csv   # мінімум для аналізу
│       ├── features_hourly.csv
│       └── features_1m.csv
```

**Підсумок:** для роботи тільки з Colab достатньо завантажити в `data/processed/` файл **features_daily.csv** (його генеруєш локально разом із `build_features.py`), далі в ноутбуку працюєш уже з цими CSV.
