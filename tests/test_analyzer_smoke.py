import pandas as pd
from app.analyzer import analyze_dataframe

def test_analyze_dataframe_smoke():
    df = pd.DataFrame([
        {"date": "2025-12-01", "description": "Salary", "category": "Income", "amount": 1000.0},
        {"date": "2025-12-02", "description": "MERCADONA", "category": "Groceries", "amount": -50.0},
        {"date": "2025-12-03", "description": "RECARGA TRANSP", "category": "Transport", "amount": -10.0},
    ])
    df["date"] = pd.to_datetime(df["date"])
    result = analyze_dataframe(df)

    assert result.summary.n_transactions == 3
    assert result.summary.total_income == 1000.0
    assert result.summary.total_expenses == -60.0
    assert round(result.summary.net_balance, 2) == 940.0
    assert len(result.categories) >= 2
