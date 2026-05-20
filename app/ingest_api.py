from fastapi import APIRouter, Header, HTTPException

router = APIRouter()


@router.post("/api/ingest")
async def trigger_ingest(x_api_key: str = Header(...)):
    from app.config import settings
    if x_api_key != settings.ingest_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    from ingest import run_ingestion
    await run_ingestion()
    return {"status": "ok", "message": "Ingestion complete"}
