import pandas as pd
from datetime import datetime
from app.analyzer import compute_budget_plan


def test_budget_plan_allocates_remaining_budget():
    df = pd.DataFrame([
        {"date": "2025-12-01", "category": "Groceries", "amount": -100},
        {"date": "2025-12-02", "category": "Transport", "amount": -50},
    ])
    df["date"] = pd.to_datetime(df["date"])

    plan = compute_budget_plan(
        df,
        monthly_income=500,
        days_in_month=30,
        current_day=10,
    )

    assert plan.remaining_budget == 350
    assert len(plan.categories) == 2
