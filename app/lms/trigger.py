from fastapi import APIRouter, Query
from app.db.session import SessionLocal
from app.db.models import SDKCommand
import uuid, json

router = APIRouter()

@router.post("/trigger-entry")
def trigger_entry(lab_id: str = Query(...)):
    db = SessionLocal()

    entry_id = f"E-{uuid.uuid4().hex[:12]}"

    cmd = SDKCommand(
        sdk_id=f"SDK-NET-01",
        lab_id=lab_id,
        command="CAPTURE_ENTRY",
        payload=json.dumps({"entry_id": entry_id}),
        status="PENDING"
    )

    db.add(cmd)
    db.commit()
    db.close()

    return {"entry_id": entry_id}
