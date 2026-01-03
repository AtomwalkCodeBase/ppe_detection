from fastapi import APIRouter, Depends
from app.auth.sdk_auth import verify_sdk_key
from app.ai.ppe_detector import PPEDetector
from app.ai.decision_engine import DecisionEngine
from app.db.session import SessionLocal
from app.db.models import EntryResult, SDKCommand
from app.utils.snapshot import upload_to_s3
from app.integrations.atomwalk_client import upload_to_atomwalk

import base64
import cv2
import json
import numpy as np
import os
from datetime import datetime

router = APIRouter()

ppe = PPEDetector()
decision_engine = DecisionEngine()


@router.post("/ingest")
def ingest(payload: dict, sdk=Depends(verify_sdk_key)):
    sdk_id = sdk["sdk_id"]

    lab_id = payload["lab_id"].upper()
    entry_id = payload["entry_id"]
    user_id = payload.get("user_id", "E-1001")

    img_bytes = base64.b64decode(payload["frames"][0])
    np_img = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    detection, annotated = ppe.detect(frame)

    detected_objects = ["person"] if detection.get("person_detected") else []
    detected_objects += detection.get("ppe_detected", [])

    decision = decision_engine.evaluate(lab_id, detected_objects)

    violation = decision["status"]

    snapshot_url = upload_to_s3(
        annotated,
        lab_id=lab_id,
        entry_id=entry_id
    )

    try:
        tmp_path = f"/tmp/{entry_id}.jpg"
        cv2.imwrite(tmp_path, annotated)

        upload_to_atomwalk(
            image_path=tmp_path,
            violation=violation,
            lab_id=lab_id
        )

        os.remove(tmp_path)

    except Exception as e:
        print("Atomwalk upload failed:", str(e))

    db = SessionLocal()

    db.add(
        EntryResult(
            entry_id=entry_id,
            user_id=user_id,
            lab_id=lab_id,
            violation=violation,
            snapshot_url=snapshot_url,
            created_at=datetime.utcnow()
        )
    )

    cmd = (
        db.query(SDKCommand)
        .filter(
            SDKCommand.sdk_id == sdk_id,
            SDKCommand.lab_id == lab_id,
            SDKCommand.status == "SENT"
        )
        .first()
    )

    if cmd:
        cmd.status = "DONE"
        cmd.result = json.dumps({
            "status": decision["status"],
            "overall": decision["overall"],
            "ppe_status": decision["ppe_status"],
            "snapshot_url": snapshot_url
        })

    db.commit()
    db.close()

    return {
        "status": decision["status"],
        "overall": decision["overall"],
        "ppe_status": decision["ppe_status"],
        "snapshot_url": snapshot_url
    }
