from pathlib import Path

from app.csv_parser import parse_statement_csv
from app.analyzer import analyze_dataframe


def main():
    csv_path = Path("Export_11-12-2025-15-18-44.csv")  # change name if needed

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path.resolve()}")
        return

    with csv_path.open("rb") as f:
        file_bytes = f.read()

    df = parse_statement_csv(file_bytes)
    print("=== Parsed DataFrame (first 5 rows) ===")
    print(df.head())

    analysis = analyze_dataframe(df)

    print("\n=== Summary ===")
    print(analysis.summary)

    print("\n=== Categories ===")
    for cat in analysis.categories:
        print(cat)

    print("\n=== Top Expenses ===")
    for tx in analysis.top_expenses:
        print(tx)

    print("\n=== Insights ===")
    for line in analysis.insights:
        print("-", line)


if __name__ == "__main__":
    main()
