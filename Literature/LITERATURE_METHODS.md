# Методи з літератури та наш підхід / Literature methods and our approach

## 1. Що є в папці Literature

Є **replication package** статті:

- **Augustin P., Rubtsov A., Shin D.** (2023). *The impact of derivatives on spot markets: Evidence from the introduction of bitcoin futures contracts.* Management Science.  
- Код: Stata (`MS_Code_ARS_2023.do`), MATLAB (Figure 3). Дані — місячна частота, пари бірж (exchange–currency).

---

## 2. Які методи використовуються в статті (Augustin et al.)

### 2.1 Ідентифікація впливу

- **Difference-in-Differences (DiD):**
  - **Treatment:** біржові пари з валютою BTC-USD (де запустили ф’ючерси).
  - **Control:** інші валютні пари (наприклад BTC-EUR) без ф’ючерсів у той самий час.
  - **Post:** після введення ф’ючерсів (зокрема січень 2018).
  - Ключовий коефіцієнт: **Treatment × Post** у регресії — це оцінка causal effect введення деривативів.

### 2.2 Регресії

- **Модель:** `reghdfe` (fixed effects), залежна змінна — метрика ринку.
- **Фіксовані ефекти:** пара бірж (`ExchangePair`), місяць (`monthdummy`), валюта (`CurrencyPair`); варіанти з `ExchangePair#monthdummy` (pair-specific time FE).
- **Кластеризація SE:** по парі бірж (`cluster i.ExchangePair_`).
- **Винсоризація:** основні змінні (наприклад PriceSynchronicity_3m, PriceIntegration_3m) винсоризуються (зменшення впливу викидів).

### 2.3 Результати (залежні змінні)

- **Кореляція / інтеграція:** Price Synchronicity (rho), Price Integration (kappa) — за 3 місяці та 14 днів; окремо weekday/weekend, hourly.
- **Ліквідність:** Roll, CHL (bid-ask), Amihud, агрегована illiquidity (lambda).
- **Якість ринку:** Q (market quality), D1 (price efficiency).
- **Волатильність:** sigma (Volatility_3m).
- **Обсяг:** Volume; також взаємодія Treatment_Post × HighVolume14d.

### 2.4 Інші прийоми

- **Виключення періоду антиципації:** липень–грудень 2017 (до запуску ф’ючерсів).
- **Виключення перекривання:** січень–лютий 2018 виключені, бо 3-місячні вікна змішують pre- і post-період.
- **Event-study динаміка (Figure 3):** квартальні дами (Treatment × Q_2016Q3, …, Q_2018Q4) — перевірка паралельних трендів і динаміки ефекту.
- **Канали (Table 10):** triple differences — Treatment × Post × (Short Selling, Arbitrage Risk, Capital Controls, Attention).
- **Flow-дані (Table 8):** log(transfer) між біржами на Post, Treatment_Post.

---

## 3. Яким методом ми виявляємо вплив у нашому дослідженні

У нас **немає контрольной групи** (немає аналога «іншої валюти» без нового дериватива для того самого активу). Є лише GLD/SLV до і після запуску Binance XAUUSDT/XAGUSDT. Тому ми **не використовуємо DiD**, а проводимо **event study у формі pre/post з регресіями**.

### 3.1 Назва методу

- **Event study з pre/post порівнянням та OLS з дамою події та контролями.**

### 3.2 Що робимо

1. **Pre/post таблиця:** середні (mean) по метриках до події (pre) і після (post), окремо для GLD і SLV.
2. **t-тести:** перевірка, чи відрізняються середні pre vs post (двохвибірковий t-test).
3. **OLS-регресії:**
   - Залежні змінні: волатильність (наприклад `vol_realized_20_ret_gld`, `vol_realized_20_ret_slv`), опційно |returns|.
   - Регресори: **post_event** (0/1 після 2026-01-05), **dxy_ret**, **vix_ret**, **tnx_ret** (контролі).
   - Коефіцієнт при **post_event** інтерпретується як зміна рівня метрики після запуску перпетуалів при фіксованих рухах DXY, VIX, 10Y.
4. **Інтеграція:** тільки описово (rolling correlation GLD–XAU, SLV–XAG) після події; pre-періоду для Binance немає, тому формального тесту «інтеграція зросла» не робимо.

### 3.3 Висновок щодо методу

- **Вплив на ринок виявляємо** через:  
  (1) порівняння середніх pre/post і t-тести,  
  (2) **коефіцієнт post_event в OLS** при контролі на dxy_ret, vix_ret, tnx_ret.  
- Це типовий **event study без контрольной групи**: один ринок (ETF) у часі, подія = дата запуску; «ефект» = зміна рівня outcome після події з урахуванням контролів.

---

## 4. Що можна імплементувати з літератури

| Ідея з статті | Що зробити у нас | Складність |
|---------------|------------------|------------|
| **Винсоризація** | Винсоризувати залежні змінні (наприклад vol, Amihud) на 1–5% та 95–99% перед регресіями. | Легко |
| **Виключення перекривання** | У регресіях виключити перші ~20 днів після події (бо 20-day rolling змішує pre/post). Robustness. | Легко |
| **Event-time динаміка** | Замість одного post_event додати тижневі/двотижневі дами після події (тиждень 1, 2, …) і показати графік коефіцієнтів. | Помірно |
| **HAC (Newey–West) SE** | У часових рядах кластеризація не за одиницею, а скориговані SE на автокореляцію (statsmodels: `cov_type='HAC'`). | Легко |
| **Додаткові метрики ліквідності** | Roll, CHL потребують bid-ask; ми вже маємо Amihud і volume — можна лише явно порівняти з літературою в тексті. | Описово |

### Рекомендації

1. **Обов’язково:** у звіті чітко назвати метод: *event study, pre/post + OLS з дамою події (post_event) та контролями (DXY, VIX, 10Y); вплив = коефіцієнт post_event.*
2. **Бажано:** додати винсоризацію outcome-змінних перед регресіями (хоч на 5%/95%) і, за можливості, HAC SE для OLS.
3. **Опційно:** robustness — регресії без перших 20 днів після події; або короткий event-study графік (коефіцієнти по тижнях після події).

---

## 5. Джерела

- Augustin P., Rubtsov A., Shin D. (2023). The impact of derivatives on spot markets: Evidence from the introduction of bitcoin futures contracts. *Management Science.* Replication: `Literature/replication_package_MS-SPI-22-01939/`.
- MacKinlay A.C. (1997). Event studies in economics and finance. *Journal of Economic Literature* — класичний огляд event study.
- У проєкті: `REFERENCES.md` — посилання на статтю та методологію.
