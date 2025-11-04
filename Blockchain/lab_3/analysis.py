#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE = "https://api.etherscan.io/v2/api"

def fetch_tx(address, api_key, startblock=0, endblock=99999999, sort="asc", page_size=10000):
    page, rows = 1, []
    while True:
        url = (f"{BASE}?chainid=1&module=account&action=txlist&address={address}"
               f"&startblock={startblock}&endblock={endblock}&page={page}"
               f"&offset={page_size}&sort={sort}&apikey={api_key}")
        r = requests.get(url, timeout=30).json()
        if r.get("status") == "0" and (r.get("result") == [] or "No transactions" in r.get("message","")):
            break
        result = r.get("result") or []
        if not isinstance(result, list):
            break
        rows.extend(result)
        if len(result) < page_size:
            break
        page += 1
        time.sleep(0.21)
    return pd.DataFrame(rows)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    keep = [c for c in ["hash","blockNumber","timeStamp","from","to","value","gas","gasPrice","isError","txreceipt_status"] if c in df.columns]
    df = df[keep].copy()
    for c in ["blockNumber","gas","gasPrice"]:
        if c in df: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("int64")
    if "timeStamp" in df:
        df["timestamp"] = pd.to_datetime(pd.to_numeric(df["timeStamp"], errors="coerce"), unit="s", utc=True)
    if "value" in df:
        df["value_eth"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)/1e18
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df

def analyze(df: pd.DataFrame, wallet: str):
    if df.empty:
        return dict(total_transactions=0, average_value=0.0, max_value=0.0, min_value=0.0,
                    first_tx=None, last_tx=None, unique_senders=0, unique_receivers=0,
                    sent_eth_total=0.0, received_eth_total=0.0)
    v = df["value_eth"].astype(float)
    w = wallet.lower()
    out_m = df["from"].str.lower().eq(w)
    in_m = df["to"].str.lower().eq(w)
    return dict(
        total_transactions=int(len(df)),
        average_value=float(v.mean()),
        max_value=float(v.max()),
        min_value=float(v.min()),
        first_tx=df["timestamp"].min(),
        last_tx=df["timestamp"].max(),
        unique_senders=int(df.loc[in_m, "from"].str.lower().nunique()),
        unique_receivers=int(df.loc[out_m, "to"].str.lower().nunique()),
        sent_eth_total=float(df.loc[out_m, "value_eth"].sum()),
        received_eth_total=float(df.loc[in_m, "value_eth"].sum()),
    )

def plot_hist(df, out_path: Path):
    if df.empty: return None
    plt.figure()
    plt.hist(df["value_eth"].astype(float), bins=50)
    plt.title("Розподіл значень транзакцій (ETH)")
    plt.xlabel("Сума (ETH)")
    plt.ylabel("Кількість транзакцій")
    p = out_path / "hist_value_eth.png"
    plt.tight_layout(); plt.savefig(p, dpi=160); plt.close()
    return p

def plot_ts(df, out_path: Path):
    if df.empty: return None
    ts = df.set_index("timestamp")["value_eth"].astype(float).resample("1D").sum()
    plt.figure()
    ts.plot(kind="line", title="Сума транзакцій по днях (ETH)")
    plt.xlabel("Дата (UTC)")
    plt.ylabel("Сума за день (ETH)")
    p = out_path / "timeseries_daily_sum_eth.png"
    plt.tight_layout(); plt.savefig(p, dpi=160); plt.close()
    return p

def write_report(stats, address, out_dir: Path):
    p = out_dir / "report.md"
    def fmt(x):
        if x is None or pd.isna(x): return "-"
        u = pd.to_datetime(x)
        return u.strftime('%Y-%m-%d %H:%M:%S %Z')
    md = f"""# Звіт з аналізу транзакцій Ethereum

**Адреса:** `{address}`
**Дата генерації:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}

## Результати
- Транзакцій: **{stats['total_transactions']}**
- Середня (ETH): **{stats['average_value']:.6f}**
- Макс (ETH): **{stats['max_value']:.6f}**
- Мін (ETH): **{stats['min_value']:.6f}**
- Перша: **{fmt(stats['first_tx'])}**
- Остання: **{fmt(stats['last_tx'])}**
- Надіслано (ETH): **{stats['sent_eth_total']:.6f}**
- Отримано (ETH): **{stats['received_eth_total']:.6f}**
- Унікальних відправників: **{stats['unique_senders']}**
- Унікальних отримувачів: **{stats['unique_receivers']}**

## Файли
- transactions_clean.csv
- hist_value_eth.png
- timeseries_daily_sum_eth.png
"""
    p.write_text(md, encoding="utf-8")
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--address", required=True)
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--out", default="output_eth")
    ap.add_argument("--startblock", type=int, default=0)
    ap.add_argument("--endblock", type=int, default=99999999)
    ap.add_argument("--sort", choices=["asc","desc"], default="asc")
    ap.add_argument("--page-size", type=int, default=10000)
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    df = fetch_tx(a.address, a.api_key, a.startblock, a.endblock, a.sort, a.page_size)
    tx = clean(df)
    tx.to_csv(out / "transactions_clean.csv", index=False)
    stats = analyze(tx, a.address)
    plot_hist(tx, out)
    plot_ts(tx, out)
    write_report(stats, a.address, out)
    print("Готово ✔")

if __name__ == "__main__":
    main()