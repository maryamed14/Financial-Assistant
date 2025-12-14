from io import BytesIO
import pandas as pd


def _classify_transaction(description: str, amount: float) -> str:
    """
    Simple heuristic to assign a category based on text and sign of amount.
    You can refine this later.
    """
    desc = str(description).upper()

    if amount > 0:
        return "Income"

    # Basic keyword rules for expenses
    if any(kw in desc for kw in ["MERCADONA", "FROIZ", "ALCAMPO", "CARREFOUR"]):
        return "Groceries"

    if "RECARGA TRANSP" in desc or "VITRASA" in desc or "TAXI" in desc:
        return "Transport"

    if "METLIFE" in desc or "INSURANCE" in desc:
        return "Insurance"

    if any(kw in desc for kw in ["NETFLIX", "SPOTIFY", "OPENAI", "GOOGLE", "MICROSOFT"]):
        return "Online Services"

    return "Uncategorized"


def parse_statement_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Parse a bank CSV export with ';' delimiter into a normalized DataFrame
    with columns: date, description, category, amount.
    """
    # 1) Read CSV with the correct delimiter
    df_raw = pd.read_csv(BytesIO(file_bytes), sep=";")

    # We expect at least these columns:
    expected_cols = {"Date", "Concept", "Amount"}
    missing = expected_cols - set(df_raw.columns)
    if missing:
        raise ValueError(
            "CSV missing required columns: "
            + ", ".join(sorted(missing))
            + f". Found columns: {list(df_raw.columns)}"
        )

    df = df_raw.copy()

    # 2) Amount: from "-10.0 EUR" -> -10.0
    try:
        df["amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace(" EUR", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )
    except Exception:
        raise ValueError("Could not parse 'Amount' column. Expected values like '-10.0 EUR'.")

    # 3) Date: prefer "Operation date" (ISO) if available
    if "Operation date" in df.columns:
        df["date"] = pd.to_datetime(df["Operation date"].str[:10], errors="coerce")
    else:
        # "Date" is likely DD-MM-YYYY in your export
        df["date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # 4) Description
    df["description"] = df["Concept"].astype(str)

    # 5) Category from heuristic
    df["category"] = [
        _classify_transaction(desc, amt)
        for desc, amt in zip(df["description"], df["amount"])
    ]

    # 6) Keep normalized columns and drop invalid rows
    df_norm = df[["date", "description", "category", "amount"]].dropna(
        subset=["date", "amount"]
    )

    if df_norm.empty:
        raise ValueError("No valid transactions found in CSV.")

    return df_norm
