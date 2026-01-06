from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.auth.sdk_auth import verify_sdk_key

router = APIRouter()

@router.post("/heartbeat")
def sdk_heartbeat(
    sdk: dict = Depends(verify_sdk_key),
    db: Session = Depends(get_db),
):
    db.execute(
        text("""
            UPDATE sdks
            SET last_heartbeat = :ts,
                status = 'ACTIVE'
            WHERE id = :sdk_id
        """),
        {
            "ts": datetime.utcnow(),
            "sdk_id": sdk["sdk_id"],   # ✅ FIX IS HERE
        }
    )
    db.commit()
    return {"status": "ok"}
