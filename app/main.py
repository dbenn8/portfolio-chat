from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.chat import router as chat_router
from app.ingest_api import router as ingest_router

app = FastAPI(title="Dan Bennett Portfolio + Chat API")

app.include_router(chat_router)
app.include_router(ingest_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
