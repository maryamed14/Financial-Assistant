from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .csv_parser import parse_statement_csv
from .analyzer import analyze_dataframe
from .models import AnalysisResult


app = FastAPI(title="Financial Assistant Backend")

# CORS so React (later) can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze-statement", response_model=AnalysisResult)
async def analyze_statement(statement: UploadFile = File(...)):
    """
    Accept a CSV bank statement, analyze it and return structured insights.
    """
    filename = statement.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        file_bytes = await statement.read()
        df = parse_statement_csv(file_bytes)
        analysis = analyze_dataframe(df)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error processing the statement.")

    return analysis
