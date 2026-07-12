from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:  # noqa: BLE001 - health check must never raise
        database_status = "unavailable"

    return {
        "status": "ok" if database_status == "connected" else "degraded",
        "database": database_status,
    }
