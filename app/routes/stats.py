from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImageRecord
from app.schemas import StatsResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    records = db.query(ImageRecord).all()
    total = len(records)
    failed = len([r for r in records if r.status == "failed"])
    success = len([r for r in records if r.status == "success"])
    durations = [r.processing_time_seconds for r in records if r.processing_time_seconds is not None]

    success_rate = f"{(success / total * 100):.2f}%" if total else "0.00%"
    avg_duration = round(sum(durations) / len(durations), 4) if durations else 0.0

    return {
        "status": "success",
        "data": {
            "total": total,
            "failed": failed,
            "success_rate": success_rate,
            "average_processing_time_seconds": avg_duration,
        },
        "error": None,
    }
