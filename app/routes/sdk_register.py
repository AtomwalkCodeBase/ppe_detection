import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter()

@router.post("/register")
def register_sdk(payload: dict, db=Depends(get_db)):
    tenant_id = payload.get("tenant_id")
    network_code = payload.get("network_code")

    if not tenant_id or not network_code:
        raise HTTPException(
            status_code=400,
            detail="tenant_id and network_code are required"
        )

    # 1️⃣ Check if SDK already exists
    existing = db.execute(
        text("""
            SELECT id FROM sdks
            WHERE tenant_id = :tenant_id
              AND network_code = :network_code
        """),
        {
            "tenant_id": tenant_id,
            "network_code": network_code
        }
    ).fetchone()

    if existing:
        return {"sdk_id": existing.id}

    # 2️⃣ Create new SDK
    sdk_id = f"SDK-{uuid.uuid4()}"

    db.execute(
        text("""
            INSERT INTO sdks (id, tenant_id, network_code, status)
            VALUES (:id, :tenant_id, :network_code, 'ACTIVE')
        """),
        {
            "id": sdk_id,
            "tenant_id": tenant_id,
            "network_code": network_code
        }
    )

    db.commit()
    return {"sdk_id": sdk_id}
