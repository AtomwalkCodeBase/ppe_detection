from fastapi import Header, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db

def verify_sdk_key(
    x_sdk_key: str = Header(...),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT id, tenant_id, network_code
            FROM sdks
            WHERE id = :sdk_id
              AND status = 'ACTIVE'
        """),
        {"sdk_id": x_sdk_key}
    ).fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid SDK key")

    # ✅ ALWAYS return dict
    return {
        "sdk_id": row.id,
        "tenant_id": row.tenant_id,
        "network_code": row.network_code,
    }
