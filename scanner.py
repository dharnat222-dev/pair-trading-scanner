from pathlib import Path

print("=" * 50)
print("PAIR TRADING SCANNER V1")
print("=" * 50)

file = Path("fno_stocks.txt")

if not file.exists():
    print("ERROR : fno_stocks.txt not found")
    exit()

symbols = []

with open(file, "r") as f:
    for line in f:
        s = line.strip()
        if s:
            symbols.append(s)

print(f"Total Symbols : {len(symbols)}")

print("\nFirst 10 Symbols\n")

for s in symbols[:10]:
    print(s)

print("\nScanner Ready...")
