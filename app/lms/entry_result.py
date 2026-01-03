from fastapi import APIRouter
from app.db.session import SessionLocal
from app.db.models import EntryResult
import json

router = APIRouter()

@router.get("/entry-result/{entry_id}")
def get_result(entry_id: str):
    db = SessionLocal()
    row = db.query(EntryResult).filter(
        EntryResult.entry_id == entry_id
    ).first()
    db.close()

    if not row:
        return {"status": "PROCESSING"}

    result = {}
    try:
        result = json.loads(row.result) if row.result else {}
    except Exception:
        pass

    return {
        "status": row.violation,
        "ppe_status": result.get("ppe_status", {}),
        "snapshot_url": row.snapshot_url
    }
