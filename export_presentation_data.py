#!/usr/bin/env python3
"""
Export data and figures for the HTML presentation.
Run from project root: python3 export_presentation_data.py

Creates:
  - presentation_figures/*.png (charts)
  - presentation_data_embed.js (key results table for HTML)
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROC_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUT_DIR = os.path.join(PROJECT_ROOT, "presentation_figures")
os.makedirs(OUT_DIR, exist_ok=True)

COLORS = {
    "gld": "#B8860B", "slv": "#708090", "xau": "#DAA520", "xag": "#C0C0C0",
    "xauusdt": "#C9A227", "xagusdt": "#0D9488",  # Binance: amber and teal (distinct from SLV grey)
    "event": "#C41E3A", "pre": "#2E86AB", "post": "#E94F37",
}

def main():
    path = os.path.join(PROC_DIR, "features_daily.csv")
    if not os.path.exists(path):
        print(f"Not found: {path}. Run build_features.py first.")
        return
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
    event_date = pd.Timestamp("2026-01-05")
    core_cols = ["px_gld_close", "px_slv_close", "ret_gld", "ret_slv"]
    df = df.dropna(subset=core_cols).copy()
    df["post_event"] = (df.index >= event_date).astype(int)
    pre = df["post_event"] == 0
    post = df["post_event"] == 1

    # --- 0. Conceptual diagram: Before / After (for slide "Why this story matters") ---
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    for ax in axes:
        ax.set_axis_off()
    # Before: one venue
    axes[0].text(0.5, 0.7, "Before event", ha="center", fontsize=14, fontweight="bold")
    axes[0].text(0.5, 0.45, "ETF only\n(GLD, SLV)\nregulated exchange", ha="center", fontsize=11, va="center",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor=COLORS["gld"], alpha=0.3))
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("One venue for gold/silver", fontsize=12)
    # After: two venues
    axes[1].text(0.5, 0.7, "After event (from 2026-01-05)", ha="center", fontsize=14, fontweight="bold")
    axes[1].text(0.25, 0.4, "ETF\n(GLD, SLV)", ha="center", fontsize=10, va="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["gld"], alpha=0.3))
    axes[1].text(0.75, 0.4, "Binance\n(XAU, XAG)", ha="center", fontsize=10, va="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["xau"], alpha=0.3))
    axes[1].annotate("", xy=(0.65, 0.4), xytext=(0.35, 0.4), arrowprops=dict(arrowstyle="<->", color="gray", lw=2))
    axes[1].text(0.5, 0.2, "same asset, two venues", ha="center", fontsize=9, color="gray")
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].set_title("Two venues: we ask how ETF market changed", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "why_story_two_venues.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # --- 0b. Event and method (for slide 5) ---
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
    for ax in axes:
        ax.set_axis_off()
    # Left: timeline
    axes[0].plot([0.1, 0.45], [0.5, 0.5], "o-", color=COLORS["pre"], linewidth=2, markersize=8, label="Pre")
    axes[0].plot(0.5, 0.5, "|", color=COLORS["event"], markersize=20, markeredgewidth=3)
    axes[0].text(0.5, 0.62, "Event\n2026-01-05", ha="center", fontsize=9, color=COLORS["event"])
    axes[0].plot([0.55, 0.9], [0.5, 0.5], "o-", color=COLORS["post"], linewidth=2, markersize=8, label="Post")
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0.35, 0.7)
    axes[0].set_title("Event study: one market, before/after", fontsize=11)
    axes[0].legend(loc="lower center", ncol=2, fontsize=9)
    # Right: OLS scheme
    axes[1].text(0.5, 0.75, "OLS", ha="center", fontsize=12, fontweight="bold")
    axes[1].text(0.5, 0.5, "outcome = α + β·post_event\n         + γ₁·DXY + γ₂·VIX + γ₃·10Y", ha="center", fontsize=10, va="center",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#f0f0f0", edgecolor="gray"))
    axes[1].text(0.5, 0.25, "Key coefficient: β (effect of event)", ha="center", fontsize=9, color=COLORS["event"])
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].set_title("Pre/post + controls (no DiD)", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "event_method_design.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # --- 1. Cumulative returns (Binance only from event date — no prices before) ---
    fig, ax = plt.subplots(figsize=(10, 4))
    # ETFs: full sample, index 100 at first date
    for col, lab in [("ret_gld", "GLD"), ("ret_slv", "SLV")]:
        if col not in df.columns:
            continue
        r = df[col].fillna(0)
        cum = (1 + r).cumprod()
        cum = 100 * cum / cum.iloc[0]
        ax.plot(cum.index, cum, label=lab, color=COLORS.get(lab.lower(), "#888"), linewidth=1.8)
    # Binance: only from event_date onward (no data before); index 100 at event date
    for col, lab, ckey in [("ret_xau_binance", "XAUUSDT", "xauusdt"), ("ret_xag_binance", "XAGUSDT", "xagusdt")]:
        if col not in df.columns:
            continue
        post_ret = df.loc[df.index >= event_date, col].dropna()
        if post_ret.empty:
            continue
        cum = (1 + post_ret).cumprod()
        cum = 100 * cum / cum.iloc[0]
        ax.plot(cum.index, cum, label=lab, color=COLORS.get(ckey, "#888"), linewidth=1.8)
    ax.axvline(event_date, color=COLORS["event"], linestyle="--", linewidth=1.5, label="Event")
    ax.set_ylabel("Cumulative return (index = 100)")
    ax.set_title("Cumulative returns: ETFs vs Binance perpetuals (Binance from launch only)")
    ax.legend(loc="upper left", ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "cumulative_returns.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # --- 2. Volatility and volume over time (with % growth pre→post) ---
    def _pct(pre_mean, post_mean):
        if pre_mean is None or post_mean is None or pre_mean == 0:
            return None
        return (post_mean - pre_mean) / pre_mean * 100
    vol_pct = {}
    fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    for ax in axes:
        ax.axvline(event_date, color=COLORS["event"], linestyle="--", linewidth=1.5)
    if "vol_realized_20_ret_gld" in df.columns:
        axes[0].plot(df.index, df["vol_realized_20_ret_gld"], color=COLORS["gld"], label="GLD 20d")
        m_pre = df.loc[pre, "vol_realized_20_ret_gld"].mean()
        m_post = df.loc[post, "vol_realized_20_ret_gld"].mean()
        vol_pct["GLD_20d"] = _pct(m_pre, m_post)
    if "vol_realized_20_ret_slv" in df.columns:
        axes[0].plot(df.index, df["vol_realized_20_ret_slv"], color=COLORS["slv"], label="SLV 20d")
        m_pre = df.loc[pre, "vol_realized_20_ret_slv"].mean()
        m_post = df.loc[post, "vol_realized_20_ret_slv"].mean()
        vol_pct["SLV_20d"] = _pct(m_pre, m_post)
    axes[0].set_ylabel("Volatility")
    t0 = "Realized 20d volatility"
    if vol_pct.get("GLD_20d") is not None and vol_pct.get("SLV_20d") is not None:
        t0 += f" (GLD {vol_pct['GLD_20d']:+.0f}%, SLV {vol_pct['SLV_20d']:+.0f}% post vs pre)"
    axes[0].set_title(t0)
    axes[0].legend()
    park_pct = {}
    if "vol_parkinson_gld" in df.columns:
        axes[1].plot(df.index, df["vol_parkinson_gld"], color=COLORS["gld"], label="GLD")
        m_pre, m_post = df.loc[pre, "vol_parkinson_gld"].mean(), df.loc[post, "vol_parkinson_gld"].mean()
        park_pct["GLD"] = _pct(m_pre, m_post)
    if "vol_parkinson_slv" in df.columns:
        axes[1].plot(df.index, df["vol_parkinson_slv"], color=COLORS["slv"], label="SLV")
        m_pre, m_post = df.loc[pre, "vol_parkinson_slv"].mean(), df.loc[post, "vol_parkinson_slv"].mean()
        park_pct["SLV"] = _pct(m_pre, m_post)
    axes[1].set_ylabel("Volatility")
    t1 = "Parkinson volatility"
    if park_pct.get("GLD") is not None and park_pct.get("SLV") is not None:
        t1 += f" (GLD {park_pct['GLD']:+.0f}%, SLV {park_pct['SLV']:+.0f}% post vs pre)"
    axes[1].set_title(t1)
    axes[1].legend()
    vol_vol_pct = {}
    if "vol_gld" in df.columns:
        axes[2].plot(df.index, df["vol_gld"] / 1e6, color=COLORS["gld"], label="GLD")
        m_pre, m_post = df.loc[pre, "vol_gld"].mean(), df.loc[post, "vol_gld"].mean()
        vol_vol_pct["GLD"] = _pct(m_pre, m_post)
    if "vol_slv" in df.columns:
        axes[2].plot(df.index, df["vol_slv"] / 1e6, color=COLORS["slv"], label="SLV")
        m_pre, m_post = df.loc[pre, "vol_slv"].mean(), df.loc[post, "vol_slv"].mean()
        vol_vol_pct["SLV"] = _pct(m_pre, m_post)
    axes[2].set_ylabel("Volume (M)")
    t2 = "ETF volume"
    if vol_vol_pct.get("GLD") is not None and vol_vol_pct.get("SLV") is not None:
        t2 += f" (GLD {vol_vol_pct['GLD']:+.0f}%, SLV {vol_vol_pct['SLV']:+.0f}% post vs pre)"
    axes[2].set_title(t2)
    axes[2].legend()
    plt.suptitle("Volatility and volume over time", fontsize=12, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "vol_volume.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # --- 3. Pre vs post: one chart = % change (post vs pre) for all four metrics ---
    # Message: after the event, volatility and volume went up; silver (SLV) went up more than gold (GLD).
    pct_rows = []
    for col, label, ckey in [
        ("vol_realized_20_ret_gld", "GLD 20d volatility", "gld"),
        ("vol_realized_20_ret_slv", "SLV 20d volatility", "slv"),
        ("vol_gld", "GLD volume", "gld"),
        ("vol_slv", "SLV volume", "slv"),
    ]:
        if col not in df.columns:
            continue
        pre_m, post_m = df.loc[pre, col].mean(), df.loc[post, col].mean()
        if pre_m and pre_m != 0 and not np.isnan(pre_m):
            pct = (post_m - pre_m) / pre_m * 100
            pct_rows.append({"Metric": label, "Pct": pct, "color": COLORS.get(ckey, "#555")})
    vol_data = [r for r in pct_rows if "volatility" in r["Metric"].lower()]
    vol_vol_data = [r for r in pct_rows if "volume" in r["Metric"].lower()]

    fig, ax = plt.subplots(figsize=(9, 4))
    all_rows = vol_data + vol_vol_data
    if not all_rows:
        ax.text(0.5, 0.5, "No pre/post data", ha="center", va="center", transform=ax.transAxes)
    else:
        labels = [r["Metric"] for r in all_rows]
        pcts = [r["Pct"] for r in all_rows]
        colors = [r["color"] for r in all_rows]
        y_pos = np.arange(len(labels))
        bars = ax.barh(y_pos, pcts, color=colors, height=0.55, edgecolor="white", linewidth=0.8)
        ax.axvline(0, color="gray", linewidth=0.8, linestyle="-")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10)
        ax.set_xlabel("Percent change (post vs pre event)")
        ax.set_title("After the event: how much did each metric grow?\n(Silver SLV reacts more than gold GLD → motivates H1, H2)")
        for i, (bar, pct) in enumerate(zip(bars, pcts)):
            x_pos = pct + (4 if pct >= 0 else -4)
            ha = "left" if pct >= 0 else "right"
            ax.text(x_pos, bar.get_y() + bar.get_height() / 2, f"{pct:+.0f}%", va="center", ha=ha, fontsize=10, fontweight="bold")
        xmin = min(0, min(pcts)) - 10
        xmax = max(max(pcts) + 40, 250)
        ax.set_xlim(xmin, xmax)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "pre_post_bars.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # --- 3b. Correlation matrix (relevant variables) ---
    corr_vars = [
        ("ret_gld", "GLD ret"),
        ("ret_slv", "SLV ret"),
        ("ret_xau_binance", "XAU ret"),
        ("ret_xag_binance", "XAG ret"),
        ("dxy_ret", "DXY ret"),
        ("vix_ret", "VIX ret"),
        ("tnx_ret", "TNX ret"),
        ("dgs10_ret", "10Y ret"),
        ("vol_realized_20_ret_gld", "GLD 20d vol"),
        ("vol_realized_20_ret_slv", "SLV 20d vol"),
    ]
    available = [(col, label) for col, label in corr_vars if col in df.columns]
    if len(available) >= 3:
        cols = [c for c, _ in available]
        labels = [lab for _, lab in available]
        C = df[cols].corr()
        C.index = labels
        C.columns = labels
        fig, ax = plt.subplots(figsize=(9, 7))
        im = ax.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
        ax.set_yticklabels(labels, fontsize=9)
        for i in range(len(labels)):
            for j in range(len(labels)):
                v = C.iloc[i, j]
                ax.text(j, i, f"{v:.2f}" if not np.isnan(v) else "—", ha="center", va="center", fontsize=8)
        plt.colorbar(im, ax=ax, label="Correlation")
        ax.set_title("Correlation matrix: returns, macro controls, volatility (daily panel)")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, "correlation_matrix.png"), dpi=120, bbox_inches="tight")
        plt.close()

    # --- 4. Rolling correlation (post-event only; zoomed y so 0.9–0.95 is visible) ---
    if "corr_20_gld_xau" in df.columns or "corr_20_slv_xag" in df.columns:
        fig, ax = plt.subplots(figsize=(9, 4))
        c_gld = df["corr_20_gld_xau"].dropna() if "corr_20_gld_xau" in df.columns else pd.Series(dtype=float)
        c_slv = df["corr_20_slv_xag"].dropna() if "corr_20_slv_xag" in df.columns else pd.Series(dtype=float)
        if not c_gld.empty:
            ax.plot(c_gld.index, c_gld.values, color=COLORS["gld"], linewidth=2, label="GLD–XAU (gold ETF vs Binance)")
        if not c_slv.empty:
            ax.plot(c_slv.index, c_slv.values, color=COLORS["slv"], linewidth=2, label="SLV–XAG (silver ETF vs Binance)")
        all_vals = pd.concat([c_gld, c_slv]).dropna()
        if not all_vals.empty:
            ylo = max(0.0, float(all_vals.min()) - 0.08)
            yhi = 1.02
            ax.set_ylim(ylo, yhi)
        ax.set_ylabel("Rolling 20d correlation")
        ax.set_title("Integration: ETF and Binance perpetual move together (post-launch)\n(First point ≈ 20 trading days after launch — rolling window needs 20d of data)")
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, alpha=0.3)
        if not c_gld.empty or not c_slv.empty:
            first_ts = min(
                (c_gld.index.min() if not c_gld.empty else pd.Timestamp("2099-01-01")),
                (c_slv.index.min() if not c_slv.empty else pd.Timestamp("2099-01-01")),
            )
            ax.set_xlim(first_ts - pd.Timedelta(days=2), None)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, "rolling_corr.png"), dpi=120, bbox_inches="tight")
        plt.close()

    # --- 5. Key results table (pre/post + t-test; optional OLS) ---
    from scipy import stats
    def ttest(s, post_event):
        pre_s = s[post_event == 0].dropna()
        post_s = s[post_event == 1].dropna()
        if len(pre_s) < 3 or len(post_s) < 3:
            return np.nan, np.nan
        t_stat, p = stats.ttest_ind(post_s, pre_s, equal_var=False)
        return t_stat, p

    key_metrics = [
        ("vol_realized_20_ret_gld", "GLD 20d vol", False),
        ("vol_realized_20_ret_slv", "SLV 20d vol", False),
        ("vol_gld", "GLD volume", True),
        ("vol_slv", "SLV volume", True),
        ("corr_20_gld_xau", "Corr GLD–XAU", False),
        ("corr_20_slv_xag", "Corr SLV–XAG", False),
    ]
    key_rows = []
    base_controls = ["dxy_ret", "vix_ret", "tnx_ret"]
    if "dgs10_ret" in df.columns:
        base_controls.append("dgs10_ret")
    control_cols = base_controls + ["post_event"]
    for col, label, is_vol in key_metrics:
        if col not in df.columns:
            continue
        pre_m = df.loc[pre, col].mean()
        post_m = df.loc[post, col].mean()
        t_stat, pval = ttest(df[col], df["post_event"])
        pct = (post_m - pre_m) / pre_m * 100 if pre_m and pre_m != 0 and not np.isnan(pre_m) else None
        if is_vol and abs(pre_m) >= 1e6:
            pre_m, post_m = pre_m / 1e6, post_m / 1e6
        coef_str = "—"
        regp_str = "—"
        if col in ("vol_realized_20_ret_gld", "vol_realized_20_ret_slv"):
            avail = [c for c in control_cols if c in df.columns]
            if len(avail) >= 3:
                y = df[col].copy()
                X = df[avail].copy()
                valid = y.notna() & X.notna().all(axis=1)
                if valid.sum() > 20:
                    try:
                        import statsmodels.api as sm
                        X_const = sm.add_constant(X.loc[valid])
                        res = sm.OLS(y[valid], X_const, missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 5})
                        if "post_event" in res.params:
                            coef_str = round(res.params["post_event"], 4)
                            regp_str = round(res.pvalues["post_event"], 3)
                    except Exception:
                        pass
        t_display = round(float(t_stat), 3) if t_stat is not None and not np.isnan(t_stat) else "—"
        if pval is not None and not np.isnan(pval):
            p_display = "<0.001" if pval < 0.001 else round(float(pval), 4)
        else:
            p_display = "—"
        key_rows.append({
            "Metric": label,
            "Pre mean": round(float(pre_m), 6) if pre_m is not None and not np.isnan(pre_m) else "—",
            "Post mean": round(float(post_m), 6) if post_m is not None and not np.isnan(post_m) else "—",
            "Pct": f"{pct:+.0f}%" if pct is not None and not np.isnan(pct) else "—",
            "t": t_display,
            "t-test p": p_display,
            "post coef": coef_str,
            "reg p": regp_str,
        })

    # Write embed JS for HTML
    embed_path = os.path.join(PROJECT_ROOT, "presentation_data_embed.js")
    with open(embed_path, "w", encoding="utf-8") as f:
        f.write("window.PRESENTATION_DATA = ")
        json.dump({"keyTable": key_rows}, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"Saved {embed_path}")
    print(f"Saved figures to {OUT_DIR}/")
    print("Open presentation_draft.html in a browser to view charts and table.")


if __name__ == "__main__":
    main()
