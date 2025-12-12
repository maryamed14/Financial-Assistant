import pandas as pd
from app.analyzer import compute_month_pacing_forecast

def test_month_pacing_forecast_basic():
    df = pd.DataFrame([
        {"date": "2025-11-01", "description": "A", "category": "Groceries", "amount": -10.0},
        {"date": "2025-11-02", "description": "B", "category": "Groceries", "amount": -20.0},
        {"date": "2025-11-03", "description": "C", "category": "Income", "amount": 100.0},
    ])
    df["date"] = pd.to_datetime(df["date"])

    forecast = compute_month_pacing_forecast(df, target_spend_limit=200.0)

    assert forecast.elapsed_days == 3
    assert forecast.days_in_month == 30  # Nov
    assert forecast.spent_so_far == 30.0
    assert forecast.projected_month_end_spend == round((30.0/3)*30, 2)  # 300.0
    assert forecast.remaining_days == 30 - 3  # remaining after Nov 3rd
    assert forecast.recommended_spend_per_day > 0
