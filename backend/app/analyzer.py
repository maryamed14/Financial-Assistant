from typing import List
import pandas as pd
from .models import (
    Summary,
    CategoryItem,
    Transaction,
    ChartData,
    UserProfileUpdate,
    AnalysisResult,
)


def compute_basic_stats(df: pd.DataFrame) -> Summary:
    total_expenses = df[df["amount"] < 0]["amount"].sum()
    total_income = df[df["amount"] > 0]["amount"].sum()
    net_balance = total_income + total_expenses

    return Summary(
        total_expenses=float(total_expenses),
        total_income=float(total_income),
        net_balance=float(net_balance),
        n_transactions=int(len(df)),
    )


def compute_category_breakdown(df: pd.DataFrame) -> List[CategoryItem]:
    expenses = df[df["amount"] < 0].copy()
    if "category" not in expenses.columns:
        expenses["category"] = "Uncategorized"

    grouped = expenses.groupby("category")["amount"].sum().sort_values()
    total_expenses = grouped.sum() or 1.0  # avoid division by zero

    items: List[CategoryItem] = []
    for category, total in grouped.items():
        percentage = (total / total_expenses) * 100
        items.append(
            CategoryItem(
                category=category,
                total_amount=float(total),
                percentage=float(percentage),
            )
        )
    return items


def compute_top_expenses(df: pd.DataFrame, n: int = 5) -> List[Transaction]:
    expenses = df[df["amount"] < 0].copy()
    top = expenses.sort_values("amount").head(n)

    result: List[Transaction] = []
    for _, row in top.iterrows():
        result.append(
            Transaction(
                date=row["date"].date().isoformat(),
                description=str(row["description"]),
                category=str(row.get("category", "Uncategorized")),
                amount=float(row["amount"]),
            )
        )
    return result


def compute_chart_data(categories: List[CategoryItem]) -> ChartData:
    cats = [c.category for c in categories]
    amounts = [abs(c.total_amount) for c in categories]
    return ChartData(categories=cats, amounts=amounts)


def infer_user_profile(df: pd.DataFrame, summary: Summary) -> UserProfileUpdate:
    total_expenses = abs(summary.total_expenses)
    total_income = summary.total_income

    monthly_income = total_income if total_income > 0 else total_expenses * 1.2
    balance = summary.net_balance
    savings_goal = max(balance * 1.5, 10000)
    current_savings = max(balance, 0)

    restaurants = df[
        (df["amount"] < 0)
        & (df["category"].str.contains("restaurant", case=False))
    ]
    restaurant_spending = abs(restaurants["amount"].sum())
    restaurant_baseline = restaurant_spending  # can change when you have history

    return UserProfileUpdate(
        balance=round(balance, 2),
        monthlyIncome=round(monthly_income, 2),
        spendingThisMonth=round(total_expenses, 2),
        savingsGoal=round(float(savings_goal), 2),
        currentSavings=round(float(current_savings), 2),
        restaurantSpending=round(float(restaurant_spending), 2),
        restaurantBaseline=round(float(restaurant_baseline), 2),
    )


def generate_insights(
    summary: Summary,
    categories: List[CategoryItem],
    user_profile: UserProfileUpdate,
) -> List[str]:
    insights: List[str] = []

    total_exp = abs(summary.total_expenses)
    total_inc = summary.total_income
    net = summary.net_balance

    if total_inc > 0:
        savings_rate = (net / total_inc) * 100
        insights.append(
            f"Your net balance for this period is {net:.2f}, which corresponds to a savings rate of {savings_rate:.1f}% of your income."
        )
    else:
        insights.append(
            f"Your total expenses are {total_exp:.2f}, but no income was detected in this statement."
        )

    if categories:
        top_cat = sorted(categories, key=lambda c: c.total_amount)[0]
        insights.append(
            f"Your highest spending category is '{top_cat.category}' with {abs(top_cat.total_amount):.2f}, representing {abs(top_cat.percentage):.1f}% of total expenses."
        )

    if user_profile.restaurantSpending > 0:
        insights.append(
            f"You spent {user_profile.restaurantSpending:.2f} on restaurants this period."
        )

    if total_inc > 0:
        remaining_budget = total_inc - total_exp
        if remaining_budget < 0:
            insights.append(
                f"You overspent your income by {-remaining_budget:.2f} in this period."
            )
        else:
            insights.append(
                f"You still have approximately {remaining_budget:.2f} available from this period's income."
            )

    return insights


def analyze_dataframe(df: pd.DataFrame) -> AnalysisResult:
    summary = compute_basic_stats(df)
    categories = compute_category_breakdown(df)
    top_expenses = compute_top_expenses(df)
    chart = compute_chart_data(categories)
    user_profile = infer_user_profile(df, summary)
    insights = generate_insights(summary, categories, user_profile)

    return AnalysisResult(
        summary=summary,
        categories=categories,
        top_expenses=top_expenses,
        chart=chart,
        user_profile=user_profile,
        insights=insights,
    )
