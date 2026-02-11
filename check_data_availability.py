#!/usr/bin/env python3
"""
Quick data availability check for the Binance gold/silver project vs ETFs.
Run: python check_data_availability.py
"""

import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

# --- 1. ETF (Yahoo Finance) ---
print("=" * 60)
print("1. ETF (Yahoo Finance): GLD, IAU, SLV, GDX, SIL")
print("=" * 60)
try:
    import yfinance as yf
    tickers = ["GLD", "IAU", "SLV", "GDX", "SIL"]
    # Period: from autumn 2025 to cover pre/post event around Jan 2026
    start = "2025-09-01"
    end = "2026-02-11"
    data = yf.download(tickers, start=start, end=end, group_by="ticker", progress=False, auto_adjust=False)
    if data is None or data.empty:
        print("  Error: data did not load (check tickers or network).")
    else:
        n = len(data)
        print(f"  Loaded {n} days. Columns (sample): {list(data.columns)[:6]}...")
        for t in tickers:
            if isinstance(data.columns, pd.MultiIndex) and t in data.columns.get_level_values(0):
                print(f"  {t}: OK")
            elif not isinstance(data.columns, pd.MultiIndex):
                print("  All tickers in a single table: OK")
                break
            else:
                print(f"  {t}: please inspect manually")
except ImportError:
    print("  yfinance is not installed: pip install yfinance")
except Exception as e:
    print(f"  Error: {e}")

# --- 2. Binance API (XAUUSDT, XAGUSDT) ---
print("\n" + "=" * 60)
print("2. Binance Futures API: XAUUSDT, XAGUSDT perpetual")
print("=" * 60)
try:
    import requests
    # Docs: continuousKlines, pair=XAUUSDT, contractType=PERPETUAL or TRADIFI_PERPETUAL
    base = "https://fapi.binance.com/fapi/v1"
    # Try both PERPETUAL and TRADIFI_PERPETUAL
    for contract_type in ["PERPETUAL", "TRADIFI_PERPETUAL"]:
        for symbol in ["XAUUSDT", "XAGUSDT"]:
            url = f"{base}/continuousKlines?pair={symbol}&contractType={contract_type}&interval=1d&limit=30"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                j = r.json()
                if isinstance(j, list) and len(j) > 0:
                    t0 = datetime.fromtimestamp(j[0][0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                    t1 = datetime.fromtimestamp(j[-1][0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                    print(f"  {symbol} ({contract_type}): OK, example dates: {t0} .. {t1}")
                    break
                else:
                    print(f"  {symbol} ({contract_type}): empty response")
            else:
                print(f"  {symbol} ({contract_type}): HTTP {r.status_code} - {r.text[:80]}")
except ImportError:
    print("  requests is not installed: pip install requests")
except Exception as e:
    print(f"  Error: {e}")

# --- 3. Funding rate Binance ---
print("\n" + "=" * 60)
print("3. Binance Funding rate (fapi)")
print("=" * 60)
try:
    import requests
    # fundingRate endpoint: /fapi/v1/fundingRate?symbol=...
    base = "https://fapi.binance.com/fapi/v1"
    for sym in ["XAUUSDT", "XAGUSDT"]:
        url = f"{base}/fundingRate?symbol={sym}&limit=10"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.json():
            print(f"  {sym} fundingRate: OK")
        else:
            print(f"  {sym} fundingRate: HTTP {r.status_code} or empty (maybe symbol is not on fapi)")
except Exception as e:
    print(f"  Error: {e}")

# --- 4. Контрольні змінні: DXY, VIX, 10Y (Yahoo) ---
print("\n" + "=" * 60)
print("4. Control variables (Yahoo): DXY, ^VIX, ^TNX")
print("=" * 60)
try:
    import yfinance as yf
    ctrl = yf.download(["DX-Y.NYB", "^VIX", "^TNX"], start="2025-09-01", end="2026-02-11", progress=False, group_by="ticker")
    if ctrl is not None and not ctrl.empty:
        print("  DX-Y.NYB (DXY), ^VIX, ^TNX: download verified (Yahoo)")
    else:
        print("  Please check tickers manually (DXY may use another ticker)")
except Exception as e:
    print(f"  Error: {e}")

# --- 5. FRED (опційно) ---
print("\n" + "=" * 60)
print("5. FRED (St. Louis Fed) - requires API key for full access")
print("=" * 60)
try:
    import pandas as pd
    # fredapi requires pip install fredapi and FRED_API_KEY
    from fredapi import Fred
    fred = Fred(api_key=None)  # without key there may be limitations
    print("  fredapi: install fredapi and set FRED_API_KEY for DGS10, DEXUSEU, etc.")
except ImportError:
    print("  fredapi is not installed. Alternative: DXY/VIX/10Y via yfinance is enough for the course.")

print("\n" + "=" * 60)
print("Summary: see output above. If Binance returns 400 for XAUUSDT/XAGUSDT, contracts may be on a separate regional API (Nest/ADGM).")
print("=" * 60)
