
from fastapi.testclient import TestClient
from app.main import app, MAX_UPLOAD_BYTES

client = TestClient(app)

def test_rejects_non_csv_extension():
    files = {"statement": ("statement.txt", b"hello", "text/plain")}
    r = client.post("/api/analyze-statement", files=files)
    assert r.status_code == 400
    assert "CSV" in r.json()["detail"]

def test_rejects_missing_required_columns():
    bad_csv = b"foo;bar;baz\n1;2;3\n"
    files = {"statement": ("statement.csv", bad_csv, "text/csv")}
    r = client.post("/api/analyze-statement", files=files)
    assert r.status_code == 400
    assert "missing required columns" in r.json()["detail"].lower()

def test_rejects_too_large_file():
    big = b"a" * (MAX_UPLOAD_BYTES + 1)
    files = {"statement": ("statement.csv", big, "text/csv")}
    r = client.post("/api/analyze-statement", files=files)
    assert r.status_code == 413

