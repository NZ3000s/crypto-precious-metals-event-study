# Twitter thread: Binance gold/silver perpetuals & ETF markets

**Use this for your researcher blog / Twitter.** Short, simple language. Each block = one tweet (keep under 280 characters if you post as separate tweets). Charts are in `presentation_figures/` — run `python3 export_presentation_data.py` if you need to regenerate them.

---

## Thread copy (tweet by tweet)

**Tweet 1 — Hook**  
When Binance listed gold and silver perpetuals (XAUUSDT, XAGUSDT), I asked: did the *old* market—the big gold/silver ETFs (GLD, SLV)—change? Short answer: yes. 🧵

**Image:** `presentation_figures/why_story_two_venues.png`  
*(Before: one venue. After: two venues. Same asset.)*

---

**Tweet 2 — Setup**  
Same stuff, two places to trade it: regulated ETFs (GLD, SLV) and now 24/7 perpetuals on a crypto exchange. I ran an event study around the launch date (Jan 5, 2026) and checked volatility, volume, and how tight the link is between the two.

**Image:** (optional) `presentation_figures/event_method_design.png`  
*(Timeline + “we control for macro” in one pic.)*

---

**Tweet 3 — Finding 1**  
After the launch, ETF volatility and trading volume went **up**—and we controlled for the dollar (DXY), VIX, and rates. So the move looks tied to the new listing, not just “markets were crazy that month.”

**Image:** `presentation_figures/pre_post_bars.png`  
*(Pre vs post % change: volatility and volume bars; silver jumps more.)*

---

**Tweet 4 — Finding 2**  
Silver (SLV) reacted harder than gold (GLD): bigger bump in volatility and volume. Same story, different intensity.

**Image:** (same as Tweet 3, or crop to SLV/GLD comparison if you have a version)

---

**Tweet 5 — Finding 3**  
Here’s the fun part: after the launch, the ETF and the Binance perpetual move **in lockstep**. Rolling correlation sits near 0.9–1. So it’s not “crypto vs traditional”—it’s one price-discovery process across two venues.

**Image:** `presentation_figures/rolling_corr.png`  
*(Rolling 20d correlation GLD–XAU, SLV–XAG; high and stable.)*

---

**Tweet 6 — So what**  
Why care? Market-makers, arbitrageurs, and regulators: same exposure, two venues, one price. New derivatives on a new venue can shift how the incumbent market behaves—same idea as Bitcoin futures and spot.

**Image:** (optional) `presentation_figures/cumulative_returns.png`  
*(All four series move together after the event.)*

---

**Tweet 7 — Takeaway**  
TL;DR: Binance listing gold/silver perpetuals didn’t leave the ETF market unchanged. Volatility and volume went up (we controlled for macro). The two venues are tightly linked. One market, two doors. 🏁

**Image:** (optional) `presentation_figures/vol_volume.png`  
*(Volatility and volume over time with event line.)*

---

## Charts quick reference

| Use for tweet | File | What it shows |
|---------------|------|----------------|
| Hook / “two venues” | `why_story_two_venues.png` | Before vs after: one venue → two venues |
| Method | `event_method_design.png` | Event timeline + OLS with controls |
| Main result | `pre_post_bars.png` | Pre vs post % change (vol & volume) |
| Integration | `rolling_corr.png` | GLD–XAU, SLV–XAG rolling correlation |
| Co-movement | `cumulative_returns.png` | ETFs + Binance cumulative returns |
| Dynamics | `vol_volume.png` | Volatility and volume over time |
| Extra | `correlation_matrix.png` | Correlation matrix of key variables |

---

## Blog version (one short post)

If you paste the thread into a **single blog post**, use this compact version. You can attach 2–3 figures (e.g. `why_story_two_venues.png`, `pre_post_bars.png`, `rolling_corr.png`).

**Title idea:** *When Binance Listed Gold and Silver Perpetuals, the ETF Market Didn’t Sit Still*

**Body (short):**  
In early 2026, Binance started listing perpetuals on gold and silver (XAUUSDT, XAGUSDT). That gave traders a second venue for the same exposure—alongside the big ETFs (GLD, SLV). We ran an event study and found that after the launch, ETF volatility and volume went up even after controlling for the dollar, VIX, and rates. Silver (SLV) reacted more than gold (GLD). And the two venues didn’t trade in isolation: rolling correlation between the ETF and the Binance perpetual is high (around 0.9–1), so they move in lockstep. Bottom line: new derivatives on a new venue can change how the old market behaves—one price-discovery process, two doors. Relevant for market-makers, arbitrageurs, and regulators.

---

## Hashtags (optional)

`#Gold` `#Silver` `#ETF` `#Crypto` `#EventStudy` `#MarketStructure` `#Binance` `#Research`
