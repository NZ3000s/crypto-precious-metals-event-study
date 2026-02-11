#!/usr/bin/env python3
"""
Build daily feature dataset for the Binance gold/silver vs ETF project.

Inputs (already downloaded by download_data.py):
    data/raw/binance_xauusdt_1m.csv
    data/raw/binance_xagusdt_1m.csv
    data/raw/binance_*_funding.csv
    data/raw/data/raw/binance_*_open_interest.csv
    data/raw/etf_gld_iau_slv_gdx_sil_daily.csv
    data/raw/controls_dxy_vix_tnx_daily.csv

Output:
    data/processed/features_daily.csv

The list and rationale of variables is documented in VARIABLES_DESCRIPTION.md.
"""

import os
from typing import Tuple

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROC_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _ensure_datetime_index(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col])
    df = df.set_index(col).sort_index()
    return df


def _compute_log_return(series: pd.Series) -> pd.Series:
    return np.log(series).diff()


def _daily_from_binance_1m(path: str, prefix: str) -> pd.DataFrame:
    """
    Aggregate Binance 1m klines to daily OHLCV for a given instrument.
    """
    df = pd.read_csv(path, parse_dates=["open_time", "close_time"])
    df["date"] = df["open_time"].dt.date
    g = df.groupby("date")

    daily = pd.DataFrame({
        "date": g["open_time"].min().values,
        f"{prefix}_open": g["open"].first().values,
        f"{prefix}_high": g["high"].max().values,
        f"{prefix}_low": g["low"].min().values,
        f"{prefix}_close": g["close"].last().values,
        f"{prefix}_volume": g["volume"].sum().values,
        f"{prefix}_num_trades": g["num_trades"].sum().values,
    })
    daily = _ensure_datetime_index(daily, "date")
    return daily


def _daily_funding_from_binance(path: str, col_prefix: str) -> pd.DataFrame:
    """
    Convert Binance funding history to daily average funding and mark price.
    """
    df = pd.read_csv(path, parse_dates=["fundingTime"])
    df["date"] = df["fundingTime"].dt.date
    g = df.groupby("date")
    daily = pd.DataFrame({
        "date": list(g.groups.keys()),
        f"funding_{col_prefix}": g["fundingRate"].mean().values,
        f"funding_mark_{col_prefix}": g["markPrice"].mean().values,
    })
    daily = _ensure_datetime_index(daily, "date")
    return daily


def _daily_oi_from_binance(path: str, col_prefix: str) -> pd.DataFrame:
    """
    Current open interest time series (may have few points) -> daily with ffill.
    """
    df = pd.read_csv(path, parse_dates=["time"])
    df["date"] = df["time"].dt.date
    g = df.groupby("date")
    daily = pd.DataFrame({
        "date": list(g.groups.keys()),
        f"oi_{col_prefix}": g["openInterest"].last().values,
    })
    daily = _ensure_datetime_index(daily, "date")
    daily = daily.asfreq("D").ffill()
    return daily


def _load_etf_daily(path: str) -> pd.DataFrame:
    """
    Load ETF CSV exported by yfinance (custom header layout) and extract
    open/high/low/close/volume for GLD and SLV.
    """
    raw = pd.read_csv(path, header=None)
    # Row 0: tickers, row 1: fields, row 2: "Date" marker, rows 3+ data.
    tickers_row = list(raw.iloc[0])
    fields_row = list(raw.iloc[1])

    data = raw.iloc[3:].reset_index(drop=True)
    # First column is dates as string
    data.columns = [
        "Date"
        if j == 0
        else f"{tickers_row[j]}_{fields_row[j]}"
        for j in range(len(tickers_row))
    ]
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date").sort_index()

    out = pd.DataFrame(index=data.index)
    # Map (ticker, field) to our column names
    mapping = {
        "GLD_Open": "px_gld_open",
        "GLD_High": "px_gld_high",
        "GLD_Low": "px_gld_low",
        "GLD_Close": "px_gld_close",
        "GLD_Volume": "vol_gld",
        "SLV_Open": "px_slv_open",
        "SLV_High": "px_slv_high",
        "SLV_Low": "px_slv_low",
        "SLV_Close": "px_slv_close",
        "SLV_Volume": "vol_slv",
    }
    for src, dst in mapping.items():
        if src in data.columns:
            out[dst] = data[src].astype(float)

    return out


def _load_controls_daily(path: str) -> pd.DataFrame:
    """
    Load DXY, VIX, TNX daily from yfinance CSV (similar layout as ETF file).
    """
    raw = pd.read_csv(path, header=None)
    tickers_row = list(raw.iloc[0])
    fields_row = list(raw.iloc[1])
    data = raw.iloc[3:].reset_index(drop=True)
    data.columns = [
        "Date"
        if j == 0
        else f"{tickers_row[j]}_{fields_row[j]}"
        for j in range(len(tickers_row))
    ]
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date").sort_index()

    out = pd.DataFrame(index=data.index)
    mapping = {
        "DX-Y.NYB_Close": "dxy",
        "^VIX_Close": "vix",
        "^TNX_Close": "tnx",
    }
    for src, dst in mapping.items():
        if src in data.columns:
            out[dst] = data[src].astype(float)

    return out


def _add_returns_and_volatility(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Add returns, realized volatility and Parkinson/Garman–Klass measures.
    """
    df = panel.copy()

    # Returns
    df["ret_xau_binance"] = _compute_log_return(df["px_xau_binance_close"])
    df["ret_xag_binance"] = _compute_log_return(df["px_xag_binance_close"])
    df["ret_gld"] = _compute_log_return(df["px_gld_close"])
    df["ret_slv"] = _compute_log_return(df["px_slv_close"])

    # Absolute and squared returns
    for col in ["ret_xau_binance", "ret_xag_binance", "ret_gld", "ret_slv"]:
        df[f"{col}_abs"] = df[col].abs()
        df[f"{col}_sq"] = df[col] ** 2

    # Realized volatility (rolling std)
    for col, win in [("ret_xau_binance", 10), ("ret_xau_binance", 20),
                     ("ret_xag_binance", 10), ("ret_xag_binance", 20),
                     ("ret_gld", 10), ("ret_gld", 20),
                     ("ret_slv", 10), ("ret_slv", 20)]:
        df[f"vol_realized_{win}_{col}"] = df[col].rolling(win).std()

    # Parkinson volatility (high/low based)
    def parkinson_vol(high: pd.Series, low: pd.Series, window: int) -> pd.Series:
        rs = (np.log(high / low) ** 2) / (4 * np.log(2))
        return rs.rolling(window).mean().pow(0.5)

    df["vol_parkinson_gld"] = parkinson_vol(
        df["px_gld_high"], df["px_gld_low"], 20
    )
    df["vol_parkinson_slv"] = parkinson_vol(
        df["px_slv_high"], df["px_slv_low"], 20
    )
    df["vol_parkinson_xau_binance"] = parkinson_vol(
        df["px_xau_binance_high"], df["px_xau_binance_low"], 20
    )
    df["vol_parkinson_xag_binance"] = parkinson_vol(
        df["px_xag_binance_high"], df["px_xag_binance_low"], 20
    )

    # Garman–Klass volatility
    def gk_vol(open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series,
               window: int) -> pd.Series:
        log_hl = np.log(high / low)
        log_co = np.log(close / open_)
        rs = 0.5 * log_hl ** 2 - (2 * np.log(2) - 1) * log_co ** 2
        return rs.rolling(window).mean().pow(0.5)

    df["vol_gk_gld"] = gk_vol(
        df["px_gld_open"], df["px_gld_high"], df["px_gld_low"], df["px_gld_close"], 20
    )
    df["vol_gk_slv"] = gk_vol(
        df["px_slv_open"], df["px_slv_high"], df["px_slv_low"], df["px_slv_close"], 20
    )
    df["vol_gk_xau_binance"] = gk_vol(
        df["px_xau_binance_open"], df["px_xau_binance_high"],
        df["px_xau_binance_low"], df["px_xau_binance_close"], 20
    )
    df["vol_gk_xag_binance"] = gk_vol(
        df["px_xag_binance_open"], df["px_xag_binance_high"],
        df["px_xag_binance_low"], df["px_xag_binance_close"], 20
    )

    return df


def _add_integration_features(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Rolling correlations, betas, vol ratios, absolute return gaps.
    """
    df = panel.copy()

    # 20-day rolling correlations
    df["corr_20_gld_xau"] = df["ret_gld"].rolling(20).corr(df["ret_xau_binance"])
    df["corr_20_slv_xag"] = df["ret_slv"].rolling(20).corr(df["ret_xag_binance"])

    # 60-day rolling betas: cov(ret_etf, ret_binance) / var(ret_binance)
    def rolling_beta(y: pd.Series, x: pd.Series, window: int) -> pd.Series:
        cov = y.rolling(window).cov(x)
        var = x.rolling(window).var()
        return cov / var

    df["beta_60_gld_on_xau"] = rolling_beta(df["ret_gld"], df["ret_xau_binance"], 60)
    df["beta_60_slv_on_xag"] = rolling_beta(df["ret_slv"], df["ret_xag_binance"], 60)

    # Volatility ratios (20-day realized vol)
    df["vol_ratio_gld_xau"] = (
        df["vol_realized_20_ret_gld"] / df["vol_realized_20_ret_xau_binance"]
    )
    df["vol_ratio_slv_xag"] = (
        df["vol_realized_20_ret_slv"] / df["vol_realized_20_ret_xag_binance"]
    )

    # Absolute return gaps
    df["abs_return_gap_gld_xau"] = df["ret_gld_abs"] - df["ret_xau_binance_abs"]
    df["abs_return_gap_slv_xag"] = df["ret_slv_abs"] - df["ret_xag_binance_abs"]

    return df


def _add_event_dummies(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Event indicators around futures launch.
    """
    df = panel.copy()
    # Use gold launch date as main event
    event_date = pd.Timestamp("2026-01-05", tz=None)
    df["post_event"] = (df.index >= event_date).astype(int)
    df["event_window_7"] = (
        (df.index >= event_date) & (df.index < event_date + pd.Timedelta(days=7))
    ).astype(int)
    df["event_window_14"] = (
        (df.index >= event_date) & (df.index < event_date + pd.Timedelta(days=14))
    ).astype(int)
    return df


def _add_liquidity_features(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Volume, log volume, Amihud illiquidity, etc.
    """
    df = panel.copy()

    # ETFs
    for ticker in ["gld", "slv"]:
        vol_col = f"vol_{ticker}"
        if vol_col in df.columns:
            df[f"log_{vol_col}"] = np.log(df[vol_col].replace(0, np.nan))

    # Binance (aggregated volume & trades)
    for inst in ["xau_binance", "xag_binance"]:
        vcol = f"vol_{inst}"
        tcol = f"trades_{inst}"
        if f"{inst}_volume" in df.columns:
            df[vcol] = df[f"{inst}_volume"]
            df[f"log_{vcol}"] = np.log(df[vcol].replace(0, np.nan))
        if f"{inst}_num_trades" in df.columns:
            df[tcol] = df[f"{inst}_num_trades"]
            df[f"log_{tcol}"] = np.log(df[tcol].replace(0, np.nan))

    # Amihud for ETFs (|ret| / volume)
    for (ret_col, vol_col, name) in [
        ("ret_gld", "vol_gld", "gld"),
        ("ret_slv", "vol_slv", "slv"),
    ]:
        if ret_col in df.columns and vol_col in df.columns:
            df[f"amihud_{name}"] = (
                df[ret_col].abs() / df[vol_col].replace(0, np.nan)
            )
            df[f"amihud_20_{name}"] = df[f"amihud_{name}"].rolling(20).mean()

    return df


def _add_funding_oi_features(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Funding rates, open interest levels and changes.
    """
    df = panel.copy()

    for asset in ["xau", "xag"]:
        fcol = f"funding_{asset}"
        if fcol in df.columns:
            df[f"{fcol}_change"] = df[fcol].diff()
            # Funding extremes: top 5% empirical quantile
            thr = df[fcol].quantile(0.95)
            df[f"funding_extreme_{asset}"] = (df[fcol] >= thr).astype(int)

        oicol = f"oi_{asset}"
        if oicol in df.columns:
            df[f"{oicol}_change"] = df[oicol].diff()

    return df


def _add_control_features(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Control variables (levels + changes) for DXY, VIX, TNX.
    """
    df = panel.copy()
    for col in ["dxy", "vix", "tnx"]:
        if col in df.columns:
            df[f"{col}_ret"] = _compute_log_return(df[col])
    return df


def build_features() -> pd.DataFrame:
    # ETFs and controls define the master calendar (we want pre‑event ETF data as well)
    etf = _load_etf_daily(os.path.join(RAW_DIR, "etf_gld_iau_slv_gdx_sil_daily.csv"))
    controls = _load_controls_daily(
        os.path.join(RAW_DIR, "controls_dxy_vix_tnx_daily.csv")
    )
    base = etf.join(controls, how="left")

    # Binance daily OHLCV
    xau_daily = _daily_from_binance_1m(
        os.path.join(RAW_DIR, "binance_xauusdt_1m.csv"),
        prefix="px_xau_binance",
    )
    xag_daily = _daily_from_binance_1m(
        os.path.join(RAW_DIR, "binance_xagusdt_1m.csv"),
        prefix="px_xag_binance",
    )

    # Funding and open interest
    xau_funding = _daily_funding_from_binance(
        os.path.join(RAW_DIR, "binance_xauusdt_funding.csv"), "xau"
    )
    xag_funding = _daily_funding_from_binance(
        os.path.join(RAW_DIR, "binance_xagusdt_funding.csv"), "xag"
    )
    xau_oi = _daily_oi_from_binance(
        os.path.join(RAW_DIR, "binance_xauusdt_open_interest.csv"), "xau"
    )
    xag_oi = _daily_oi_from_binance(
        os.path.join(RAW_DIR, "binance_xagusdt_open_interest.csv"), "xag"
    )

    # Merge everything on ETF/control calendar, allowing Binance fields to be NaN before listing
    df = (
        base.join(xau_daily, how="left")
        .join(xag_daily, how="left")
        .join(xau_funding, how="left")
        .join(xag_funding, how="left")
        .join(xau_oi, how="left")
        .join(xag_oi, how="left")
    ).sort_index()

    # Build feature blocks
    df = _add_returns_and_volatility(df)
    df = _add_integration_features(df)
    df = _add_event_dummies(df)
    df = _add_liquidity_features(df)
    df = _add_funding_oi_features(df)
    df = _add_control_features(df)

    return df


def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Raw data dir: {RAW_DIR}")
    print(f"Processed data dir: {PROC_DIR}")
    features = build_features()
    out_path = os.path.join(PROC_DIR, "features_daily.csv")
    features.to_csv(out_path, index=True)
    print(f"Saved features to {out_path} with shape {features.shape}")


if __name__ == "__main__":
    main()

