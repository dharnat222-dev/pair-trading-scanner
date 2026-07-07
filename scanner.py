import yfinance as yf
import pandas as pd

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
