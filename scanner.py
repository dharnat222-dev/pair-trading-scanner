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
