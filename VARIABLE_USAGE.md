# Використання змінних / Variable usage

У панелі `features_daily.csv` **87 змінних**. Нижче — де ми їх використовуємо і що можна додати.

---

## 1. Зараз використовуються в аналізі

| Категорія | Змінні | Де в analysis.qmd |
|-----------|--------|-------------------|
| **Ядро (core)** | `px_gld_close`, `px_slv_close`, `ret_gld`, `ret_slv` | Вибірка df_core, графіки цін і returns |
| **Binance ціни** | `px_xau_binance_close`, `px_xag_binance_close` | Графіки, cumulative returns |
| **Волатильність ETF** | `vol_realized_20_ret_gld`, `vol_realized_20_ret_slv`, `vol_parkinson_gld`, `vol_parkinson_slv` | Pre/post, t-тести, **регресії (y)** для 20d vol |
| **Ліквідність (обсяг)** | `vol_gld`, `vol_slv` | Pre/post таблиця, boxplots (якщо є) |
| **Інтеграція** | `corr_20_gld_xau`, `corr_20_slv_xag` | Rolling correlation plot, pre/post (описово) |
| **Подія** | `post_event` | Усі регресії, pre/post розбивка |
| **Контролі** | `dxy_ret`, `vix_ret`, `tnx_ret` | Регресії (X) |
| **Додатково** | `ret_gld_abs`, `ret_slv_abs` | Регресії (y), опційно |
| **Корелограма** | ~25 змінних (returns, vol, corr, beta, Amihud, controls, funding) | Heatmap кореляцій |

---

## 2. Є в даних, але майже не використовуються

| Змінні | Що це | Можливе використання |
|--------|--------|------------------------|
| **dgs10**, **dgs10_ret** | FRED 10Y yield | Додати **dgs10_ret** до регресій як контроль (разом з tnx_ret або замість) |
| **vol_realized_10_ret_*** | 10-денна реалізована волатильність | Pre/post таблиця, альтернативна регресія y |
| **vol_gk_gld**, **vol_gk_slv** (Garman–Klass) | Волатильність з OHLC | Pre/post, порівняння з Parkinson |
| **amihud_gld**, **amihud_20_gld**, **amihud_slv**, **amihud_20_slv** | Ілліквідність Amihud | Pre/post, **регресія y = amihud** (H2) |
| **log_vol_gld**, **log_vol_slv** | log(volume) | Регресія y = log_vol (ліквідність H2) |
| **beta_60_gld_on_xau**, **beta_60_slv_on_xag** | Rolling beta ETF на Binance | Pre/post (тільки post), опис інтеграції |
| **vol_ratio_gld_xau**, **vol_ratio_slv_xag** | Співвідношення волатильностей | Опис, корелограма вже є |
| **abs_return_gap_gld_xau**, **abs_return_gap_slv_xag** | Різниця \|ret\| ETF vs Binance | Опис, корелограма |
| **event_window_7**, **event_window_14** | 1 у перші 7/14 днів після події | Robustness: регресія з event_window замість post_event |
| **funding_xau**, **funding_xag**, **funding_xau_change**, **funding_extreme_xau** | Funding rate Binance | Додатковий контроль або окрема регресія (чи впливає funding на ETF vol) |
| **oi_xau**, **oi_xag** | Open interest | Описово (часто один снапшот) |
| **Binance vol/trades** | `px_xau_binance_volume`, `num_trades` | Опис активності Binance post-event |

---

## 3. Рекомендовані розширення

1. **Контролі:** у регресії додати **dgs10_ret** (або використовувати замість tnx_ret) — вже є в панелі.
2. **Ліквідність (H2):**  
   - Додати в pre/post і key-results: **amihud_gld**, **amihud_slv** (і/або amihud_20).  
   - Додати **регресію** y = amihud_gld (або log_vol_gld) на post_event + dxy_ret + vix_ret + tnx_ret.
3. **Волатильність:** додати в pre/post (і опційно в key table): **vol_gk_gld**, **vol_gk_slv**, **vol_realized_10_ret_gld/slv**.
4. **Інтеграція:** додати в key table (описово): **beta_60_gld_on_xau**, **beta_60_slv_on_xag** (post mean).
5. **Robustness:** одна регресія з **event_window_7** або **event_window_14** замість post_event (ефект у перші дні після запуску).

Якщо потрібно, можна також додати регресії з **funding_xau** / **funding_xag** як додатковими регресорами (чи змінюється волатильність ETF з funding).
