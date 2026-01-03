from fastapi import APIRouter, Query
from app.db.session import SessionLocal
from app.db.models import EntryResult

router = APIRouter()

@router.get("/entry-status")
def entry_status(entry_id: str = Query(...)):
    db = SessionLocal()

    result = (
        db.query(EntryResult)
        .filter(EntryResult.entry_id == entry_id)
        .first()
    )

    db.close()

    if not result:
        return {"status": "PENDING"}

    return {
        "status": "DONE",
        "entry_id": result.entry_id,
        "user_id": result.user_id,
        "lab_id": result.lab_id,
        "violation": result.violation,
        "timestamp": result.created_at.isoformat(),
        "snapshot_url": result.snapshot_url
    }
