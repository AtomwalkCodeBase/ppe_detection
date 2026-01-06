from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter()

@router.get("/commands")
def get_commands(
    x_sdk_key: str = Header(...),
    db: Session = Depends(get_db)
):
    # Validate SDK
    sdk = db.execute(
        text("""
            SELECT id
            FROM sdks
            WHERE id = :sdk_id
              AND status = 'ACTIVE'
        """),
        {"sdk_id": x_sdk_key}
    ).fetchone()

    if not sdk:
        raise HTTPException(status_code=401, detail="Invalid SDK")

    # Fetch ONE pending command
    row = db.execute(
        text("""
            SELECT id, entry_id, lab_id, command
            FROM sdk_commands
            WHERE sdk_id = :sdk_id
              AND status = 'PENDING'
            ORDER BY created_at
            LIMIT 1
        """),
        {"sdk_id": x_sdk_key}
    ).fetchone()

    if not row:
        return []

    # 🔥 MARK AS SENT
    db.execute(
        text("""
            UPDATE sdk_commands
            SET status = 'SENT'
            WHERE id = :id
        """),
        {"id": row.id}
    )
    db.commit()

    return [{
        "entry_id": row.entry_id,
        "lab_id": row.lab_id,
        "command": row.command
    }]
