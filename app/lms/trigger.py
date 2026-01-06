# app/lms/trigger.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from datetime import datetime

from app.db.session import get_db

router = APIRouter()

@router.post("/trigger-entry")
def trigger_entry(lab_id: str, db: Session = Depends(get_db)):
    """
    User clicks Enter Lab:
    - Validate lab
    - Find active SDK for same tenant
    - Create sdk_command entry
    """

    # 1️⃣ Validate lab
    lab = db.execute(
        text("""
            SELECT id, tenant_id
            FROM labs
            WHERE lab_id = :lab_id
        """),
        {"lab_id": lab_id}
    ).fetchone()

    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    tenant_id = lab.tenant_id

    # 2️⃣ Find ACTIVE SDK for same tenant
    sdk = db.execute(
        text("""
            SELECT id, network_code
            FROM sdks
            WHERE tenant_id = :tenant_id
              AND status = 'ACTIVE'
            ORDER BY last_heartbeat DESC
            LIMIT 1
        """),
        {"tenant_id": tenant_id}
    ).fetchone()

    if not sdk:
        raise HTTPException(status_code=404, detail="No active SDK found")

    sdk_id = sdk.id
    network_code = sdk.network_code

    # 3️⃣ Create command
    entry_id = str(uuid.uuid4())

    db.execute(
        text("""
            INSERT INTO sdk_commands (
                entry_id,
                sdk_id,
                lab_id,
                tenant_id,
                network_code,
                command,
                status,
                created_at
            )
            VALUES (
                :entry_id,
                :sdk_id,
                :lab_id,
                :tenant_id,
                :network_code,
                'CAPTURE_AND_ANALYZE',
                'PENDING',
                :created_at
            )
        """),
        {
            "entry_id": entry_id,
            "sdk_id": sdk_id,
            "lab_id": lab_id,
            "tenant_id": tenant_id,
            "network_code": network_code,
            "created_at": datetime.utcnow()
        }
    )

    db.commit()

    return {
        "entry_id": entry_id,
        "status": "PENDING",
        "sdk_id": sdk_id,
        "network_code": network_code
    }
