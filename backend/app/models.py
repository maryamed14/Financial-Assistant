from typing import List
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


class AnalysisResult(BaseModel):
    summary: Summary
    categories: List[CategoryItem]
    top_expenses: List[Transaction]
    chart: ChartData
    user_profile: UserProfileUpdate
    insights: List[str]
