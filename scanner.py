from result_filter import has_upcoming_result
import yfinance as yf
import pandas as pd
from sector_map import SECTOR
from statsmodels.tsa.stattools import coint
# Read F&O stock list
with open("fno_stocks.txt") as f:
    stocks = [x.strip() for x in f if x.strip()]

prices = pd.DataFrame()

for stock in stocks:
    try:
        print("Downloading:", stock)
        data = yf.download(
            stock,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if len(data) > 200:
            prices[stock] = data["Close"]

    except Exception as e:
        print(stock, e)

print()
print("Stocks Downloaded:", len(prices.columns))

prices.to_csv("prices.csv")

print("prices.csv created successfully")
print("\nCalculating Correlation...")

corr = prices.corr()

pairs = []
filtered_pairs = []

for s1, s2, corr in pairs:
    if SECTOR.get(s1) != SECTOR.get(s2):
        filtered_pairs.append([s1, s2, corr])

pairs = filtered_pairs

print(f"Pairs after sector filter: {len(pairs)}")
for i in range(len(corr.columns)):
    for j in range(i + 1, len(corr.columns)):

        s1 = corr.columns[i]
        s2 = corr.columns[j]

        c = corr.iloc[i, j]

        if c >= 0.90:
            pairs.append([s1, s2, round(c, 4)])

pairs = sorted(pairs, key=lambda x: x[2], reverse=True)

print("\nTop Correlated Pairs\n")

for p in pairs[:50]:
    print(p)

pd.DataFrame(
    pairs,
    columns=["Stock1", "Stock2", "Correlation"]
).to_csv("top_pairs.csv", index=False)

print("\ntop_pairs.csv created")
print("\nRunning Cointegration Test...\n")

good_pairs = []

for s1, s2, corr in pairs:

    try:
        score, pvalue, _ = coint(prices[s1], prices[s2])

        if pvalue < 0.05:
            good_pairs.append([
                s1,
                s2,
                round(corr,4),
                round(pvalue,6)
            ])

    except:
        pass

print("Cointegrated Pairs\n")

for p in good_pairs[:30]:
    print(p)

pd.DataFrame(
    good_pairs,
    columns=[
        "Stock1",
        "Stock2",
        "Correlation",
        "PValue"
    ]
).to_csv("cointegrated_pairs.csv", index=False)

print("\ncointegrated_pairs.csv created")
import numpy as np

print("\nCalculating Hedge Ratio...")

hedge_pairs = []

for s1, s2, corr, pvalue in good_pairs:

    try:
        beta = np.polyfit(
            prices[s2],
            prices[s1],
            1
        )[0]

        hedge_pairs.append([
            s1,
            s2,
            round(corr,4),
            round(pvalue,6),
            round(beta,4)
        ])

    except:
        pass

pd.DataFrame(
    hedge_pairs,
    columns=[
        "Stock1",
        "Stock2",
        "Correlation",
        "PValue",
        "HedgeRatio"
    ]
).to_csv("hedge_pairs.csv", index=False)

print("hedge_pairs.csv created")
print("\nCalculating Z-Score...")

zscore_pairs = []

for s1, s2, corr, pvalue, beta in hedge_pairs:

    spread = prices[s1] - beta * prices[s2]

    mean = spread.mean()
    std = spread.std()

    z = (spread.iloc[-1] - mean) / std

    zscore_pairs.append([
        s1,
        s2,
        round(corr,4),
        round(pvalue,6),
        round(beta,4),
        round(z,2)
    ])

pd.DataFrame(
    zscore_pairs,
    columns=[
        "Stock1",
        "Stock2",
        "Correlation",
        "PValue",
        "HedgeRatio",
        "ZScore"
    ]
).to_csv("zscore_pairs.csv", index=False)

print("zscore_pairs.csv created")
print("\nGenerating Trade Signals...")

signals = []

for s1, s2, corr, pvalue, beta, z in zscore_pairs:

    signal = "NO TRADE"

    if z >= 2:
        signal = f"SELL {s1} | BUY {s2}"

    elif z <= -2:
        signal = f"BUY {s1} | SELL {s2}"

    signals.append([
        s1,
        s2,
        round(corr,4),
        round(pvalue,6),
        round(beta,4),
        round(z,2),
        signal
    ])

pd.DataFrame(
    signals,
    columns=[
        "Stock1",
        "Stock2",
        "Correlation",
        "PValue",
        "HedgeRatio",
        "ZScore",
        "Signal"
    ]
).to_csv("signal_pairs.csv", index=False)

print("signal_pairs.csv created")
print("\nRanking Pairs...")

ranked = []

for s1, s2, corr, pvalue, beta, z, signal in signals:

    score = (
        (corr * 50)
        + ((1 - pvalue) * 30)
        + (max(0, 2 - abs(z)) * 10)
    )

    ranked.append([
        s1,
        s2,
        round(corr, 4),
        round(pvalue, 6),
        round(beta, 4),
        round(z, 2),
        signal,
        round(score, 2)
    ])

ranked.sort(key=lambda x: x[7], reverse=True)

import pandas as pd

df = pd.DataFrame(
    ranked,
    columns=[
        "Stock1",
        "Stock2",
        "Correlation",
        "PValue",
        "HedgeRatio",
        "ZScore",
        "Signal",
        "Score"
    ]
)

df.to_csv("final_pairs.csv", index=False)

print("\nTop 10 Best Pairs\n")

print(df.head(10))

print("\nfinal_pairs.csv created")
