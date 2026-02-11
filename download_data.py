#!/usr/bin/env python3
"""
Download raw data for the project:
- Binance TRADIFI_PERPETUAL XAUUSDT, XAGUSDT (1m interval, full available period)
- ETFs (GLD, IAU, SLV, GDX, SIL) via yfinance
- Control variables (DXY, VIX, 10Y) via yfinance
- DGS10 via FRED (if FRED_API_KEY is available)

Output: CSV files in data/raw/.

Run:
    python download_data.py
"""

import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import ssl
import urllib.error

import requests
import pandas as pd
import yfinance as yf


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------
# 1. Binance helpers
# ---------------------------------------------------------------------

BINANCE_FAPI_BASE = "https://fapi.binance.com"


def binance_continuous_klines(
    pair: str,
    contract_type: str = "TRADIFI_PERPETUAL",
    interval: str = "1m",
    start_time_ms: int = None,
    end_time_ms: int = None,
) -> pd.DataFrame:
    """
    Download all available klines for a pair/contract in a time range.
    We paginate over time (limit=1500, Binance maximum).
    """
    url = f"{BINANCE_FAPI_BASE}/fapi/v1/continuousKlines"
    params = {
        "pair": pair,
        "contractType": contract_type,
        "interval": interval,
        "limit": 1500,
    }
    if start_time_ms is None:
        # If no explicit start is provided, use contract launch date 2026-01-05.
        start_dt = datetime(2026, 1, 5, tzinfo=timezone.utc)
        start_time_ms = int(start_dt.timestamp() * 1000)
    if end_time_ms is None:
        end_time_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    all_rows: List[List[Any]] = []
    current = start_time_ms

    while current < end_time_ms:
        p = params.copy()
        p["startTime"] = current
        p["endTime"] = end_time_ms
        resp = requests.get(url, params=p, timeout=10)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        last_open_time = rows[-1][0]
        # If we did not move forward in time, break to avoid infinite loop
        if last_open_time <= current:
            break
        current = last_open_time + 1
        # Small sleep to avoid hitting API rate limits too hard
        time.sleep(0.2)

    if not all_rows:
        return pd.DataFrame()

    cols = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "num_trades",
        "taker_buy_volume", "taker_buy_quote_volume", "ignore",
    ]
    df = pd.DataFrame(all_rows, columns=cols)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    numeric_cols = ["open", "high", "low", "close", "volume",
                    "quote_volume", "num_trades",
                    "taker_buy_volume", "taker_buy_quote_volume"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["pair"] = pair
    df["interval"] = interval
    df["contract_type"] = contract_type
    return df


def binance_funding_and_oi(symbol: str) -> Dict[str, pd.DataFrame]:
    """
    Funding rate history + current open interest.
    Funding history returns up to 1000 records.
    """
    results: Dict[str, pd.DataFrame] = {}

    # Funding history
    fr_url = f"{BINANCE_FAPI_BASE}/fapi/v1/fundingRate"
    fr_params = {"symbol": symbol, "limit": 1000}
    fr_resp = requests.get(fr_url, params=fr_params, timeout=10)
    fr_resp.raise_for_status()
    fr_list = fr_resp.json()
    if fr_list:
        fr_df = pd.DataFrame(fr_list)
        fr_df["fundingTime"] = pd.to_datetime(fr_df["fundingTime"], unit="ms", utc=True)
        for c in ["fundingRate", "markPrice"]:
            fr_df[c] = pd.to_numeric(fr_df[c], errors="coerce")
        results["funding"] = fr_df

    # Current open interest
    oi_url = f"{BINANCE_FAPI_BASE}/fapi/v1/openInterest"
    oi_resp = requests.get(oi_url, params={"symbol": symbol}, timeout=10)
    oi_resp.raise_for_status()
    oi_data = oi_resp.json()
    if oi_data:
        oi_df = pd.DataFrame([oi_data])
        oi_df["time"] = pd.to_datetime(oi_df["time"], unit="ms", utc=True)
        oi_df["openInterest"] = pd.to_numeric(oi_df["openInterest"], errors="coerce")
        results["open_interest"] = oi_df

    return results


def download_binance_block() -> None:
    print("=== Binance TRADIFI_PERPETUAL XAUUSDT / XAGUSDT (1m) ===")

    # If combined file already exists, assume Binance data is downloaded
    combined_path = os.path.join(DATA_DIR, "binance_gold_silver_1m_all.csv")
    if os.path.exists(combined_path):
        print(f"  {combined_path} already exists, skipping Binance download.")
        return

    # Period from contract launch to now
    start_dt = datetime(2026, 1, 5, tzinfo=timezone.utc)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

    frames = []
    for pair in ["XAUUSDT", "XAGUSDT"]:
        print(f"Downloading klines for {pair} ...")
        df = binance_continuous_klines(pair=pair,
                                       contract_type="TRADIFI_PERPETUAL",
                                       interval="1m",
                                       start_time_ms=start_ms,
                                       end_time_ms=end_ms)
        print(f"  {pair}: {len(df)} rows")
        out_path = os.path.join(DATA_DIR, f"binance_{pair.lower()}_1m.csv")
        df.to_csv(out_path, index=False)
        frames.append(df)

        print(f"  Downloading funding/open interest for {pair} ...")
        extra = binance_funding_and_oi(symbol=pair)
        if "funding" in extra:
            extra["funding"].to_csv(
                os.path.join(DATA_DIR, f"binance_{pair.lower()}_funding.csv"),
                index=False,
            )
        if "open_interest" in extra:
            extra["open_interest"].to_csv(
                os.path.join(DATA_DIR, f"binance_{pair.lower()}_open_interest.csv"),
                index=False,
            )

    # Combined file with both instruments
    if frames:
        all_df = pd.concat(frames, ignore_index=True)
        all_path = os.path.join(DATA_DIR, "binance_gold_silver_1m_all.csv")
        all_df.to_csv(all_path, index=False)
        print(f"Total Binance 1m rows (both instruments): {len(all_df)}")


# ---------------------------------------------------------------------
# 2. ETF + control variables (yfinance)
# ---------------------------------------------------------------------

def download_yfinance_block() -> None:
    print("=== ETFs and controls (yfinance, 1d) ===")
    start = "2025-09-01"
    end = datetime.now().strftime("%Y-%m-%d")

    etf_tickers = ["GLD", "IAU", "SLV", "GDX", "SIL"]
    ctrl_tickers = ["DX-Y.NYB", "^VIX", "^TNX"]

    etf_path = os.path.join(DATA_DIR, "etf_gld_iau_slv_gdx_sil_daily.csv")
    ctrl_path = os.path.join(DATA_DIR, "controls_dxy_vix_tnx_daily.csv")

    # ETFs
    if os.path.exists(etf_path):
        print(f"  {etf_path} already exists, skipping ETF download.")
    else:
        print(f"Downloading ETFs: {etf_tickers}")
        etf = yf.download(etf_tickers, start=start, end=end,
                          progress=False, auto_adjust=False, group_by="ticker")
        etf.to_csv(etf_path)
        print(f"  ETFs: shape {etf.shape}")

    # Controls
    if os.path.exists(ctrl_path):
        print(f"  {ctrl_path} already exists, skipping controls download.")
    else:
        print(f"Downloading controls: {ctrl_tickers}")
        ctrl = yf.download(ctrl_tickers, start=start, end=end,
                           progress=False, auto_adjust=False, group_by="ticker")
        ctrl.to_csv(ctrl_path)
        print(f"  Controls: shape {ctrl.shape}")


# ---------------------------------------------------------------------
# 3. FRED (DGS10)
# ---------------------------------------------------------------------

def download_fred_block() -> None:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("=== FRED (skipped) ===")
        print("  FRED_API_KEY is not set in environment variables.")
        print("  If you want to download DGS10, run export FRED_API_KEY=... and rerun.")
        return

    out_path = os.path.join(DATA_DIR, "fred_dgs10_daily.csv")
    if os.path.exists(out_path):
        print("=== FRED DGS10 ===")
        print(f"  {out_path} already exists, skipping FRED download.")
        return

    print("=== FRED DGS10 ===")
    try:
        from fredapi import Fred
    except ImportError:
        print("  fredapi is not installed (pip install fredapi). Skipping.")
        return

    fred = Fred(api_key=api_key)
    series_id = "DGS10"
    try:
        s = fred.get_series(series_id)
    except (urllib.error.URLError, ssl.SSLCertVerificationError) as e:
        print("  Could not download DGS10 from FRED due to SSL/certificate error:")
        print(f"    {e}")
        print("  This does not affect Binance/ETF data; you can either fix macOS certificates")
        print("  or rely on DXY/VIX/TNX from yfinance as a control.")
        return
    except Exception as e:
        print(f"  Unexpected error while downloading DGS10: {e}")
        return

    df = s.to_frame(name=series_id)
    df.index.name = "date"
    df.to_csv(out_path)
    print(f"  FRED DGS10: {len(df)} rows")


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data directory: {DATA_DIR}")
    download_binance_block()
    download_yfinance_block()
    download_fred_block()
    print("=== Done. Raw data saved to data/raw/ ===")


if __name__ == "__main__":
    main()

