from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from .csv_parser import parse_statement_csv
from .analyzer import analyze_dataframe
from .models import AnalysisResult


app = FastAPI(title="Financial Assistant Backend")

# Logger setup
logger = logging.getLogger("financial-assistant")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# CORS so React (later) can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analyze-statement", response_model=AnalysisResult)
async def analyze_statement(statement: UploadFile = File(...)):
    """
    Accept a CSV bank statement, analyze it and return structured insights.
    """
    start = time.perf_counter()

    filename = statement.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        file_bytes = await statement.read()

        logger.info(
            "upload_received filename=%s content_type=%s size_bytes=%d",
            filename,
            statement.content_type,
            len(file_bytes),
        )

        df = parse_statement_csv(file_bytes)
        analysis = analyze_dataframe(df)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "analysis_completed filename=%s duration_ms=%.2f n_transactions=%d",
            filename,
            duration_ms,
            len(df),
        )

    except ValueError as e:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.warning(
            "analysis_failed filename=%s duration_ms=%.2f error=%s",
            filename,
            duration_ms,
            str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "analysis_error filename=%s duration_ms=%.2f",
            filename,
            duration_ms,
        )
        raise HTTPException(status_code=500, detail="Error processing the statement.")

    return analysis
