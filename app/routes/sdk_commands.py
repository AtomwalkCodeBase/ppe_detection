from fastapi import APIRouter, Depends, Query
from app.auth.sdk_auth import verify_sdk_key
from app.db.session import SessionLocal
from app.db.models import SDKCommand
import json

router = APIRouter()

@router.get("/commands")
def get_commands(
    lab_id: str = Query(...),
    sdk=Depends(verify_sdk_key)
):
    sdk_id = sdk["sdk_id"]
    db = SessionLocal()

    try:
        cmd = (
            db.query(SDKCommand)
            .filter(
                SDKCommand.sdk_id == sdk_id,
                SDKCommand.lab_id == lab_id,
                SDKCommand.status == "PENDING"
            )
            .order_by(SDKCommand.created_at)
            .first()
        )

        if not cmd:
            return {"command": "NONE"}

        cmd.status = "SENT"
        db.commit()

        return {
            "command": cmd.command,
            "payload": json.loads(cmd.payload)
        }

    finally:
        db.close()
