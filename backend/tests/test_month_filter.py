from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_month_query_filters_results():
    # Minimal CSV with 2 months
    csv_data = (
        "Date;Concept;Amount\n"
        "01/11/2025;MERCADONA;-10.00 EUR\n"
        "02/11/2025;MERCADONA;-20.00 EUR\n"
        "01/12/2025;MERCADONA;-5.00 EUR\n"
        "02/12/2025;Salary;100.00 EUR\n"
    ).encode("utf-8")

    files = {"statement": ("stmt.csv", csv_data, "text/csv")}

    # Ask for December
    r = client.post("/api/analyze-statement?month=2025-12", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["selected_month"] == "2025-12"
    assert "2025-11" in data["available_months"]
    assert "2025-12" in data["available_months"]

    # December expenses should be 5.00 (only one expense in Dec)
    assert abs(data["summary"]["total_expenses"]) == 5.0
