from pathlib import Path

# Read F&O stock list
stocks = []

with open("fno_stocks.txt", "r") as f:
    for line in f:
        s = line.strip()
        if s:
            stocks.append(s)

print("Total F&O Stocks:", len(stocks))
print()

for stock in stocks:
    print(stock)
