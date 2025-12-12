from typing import List, Optional
from pydantic import BaseModel


class Summary(BaseModel):
    total_expenses: float
    total_income: float
    net_balance: float
    n_transactions: int


class CategoryItem(BaseModel):
    category: str
    total_amount: float
    percentage: float


class Transaction(BaseModel):
    date: str        # ISO date string
    description: str
    category: str
    amount: float


class ChartData(BaseModel):
    categories: List[str]
    amounts: List[float]


class UserProfileUpdate(BaseModel):
    balance: float
    monthlyIncome: float
    spendingThisMonth: float
    savingsGoal: float
    currentSavings: float
    restaurantSpending: float
    restaurantBaseline: float


class Forecast(BaseModel):
    period_start: str
    period_end: str
    elapsed_days: int
    days_in_month: int
    spent_so_far: float
    projected_month_end_spend: float
    target_spend_limit: float
    remaining_days: int
    recommended_spend_per_day: float


class AnalysisResult(BaseModel):
    summary: Summary
    categories: List[CategoryItem]
    top_expenses: List[Transaction]
    chart: ChartData
    user_profile: UserProfileUpdate
    insights: List[str]
    forecast: Forecast
    available_months: List[str] = []
    selected_month: Optional[str] = None
