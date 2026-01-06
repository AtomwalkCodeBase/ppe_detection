from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import base64
import json
import cv2
import numpy as np
import tempfile
import os

from app.db.session import get_db
from app.auth.sdk_auth import verify_sdk_key
from app.ai.ppe_detector import PPEDetector
from app.utils.snapshot import upload_to_s3
from app.integrations.atomwalk_client import upload_ppe_result

router = APIRouter()

ppe_detector = PPEDetector()

@router.post("/ingest")
def sdk_ingest(
    payload: dict,
    sdk=Depends(verify_sdk_key),
    db: Session = Depends(get_db),
):
    entry_id = payload.get("entry_id")
    lab_id = payload.get("lab_id")
    frames = payload.get("frames", [])

    if not entry_id or not lab_id or not frames:
        return {"error": "Invalid payload"}

    # -------------------------------
    # Decode image
    # -------------------------------
    image_b64 = frames[0]
    img_bytes = base64.b64decode(image_b64)
    np_img = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Invalid image"}

    # -------------------------------
    # PPE detection
    # -------------------------------
    detection, annotated = ppe_detector.detect(frame)

    if not detection["person_detected"]:
        overall = "NO_PERSON"
        ppe_status = {}
    elif len(detection["ppe_detected"]) == 0:
        overall = "PPE_MISSING"
        ppe_status = {}
    else:
        overall = "PPE_OK"
        ppe_status = {p: "PASSED" for p in detection["ppe_detected"]}

    # -------------------------------
    # Upload to S3 (PERMANENT PROOF)
    # -------------------------------
    image_url = upload_to_s3(
        annotated,
        lab_id=lab_id,
        entry_id=entry_id
    )

    # -------------------------------
    # Store result in DB (SOURCE OF TRUTH)
    # -------------------------------
    db.execute(
        text("""
            INSERT INTO entry_results (
                entry_id,
                tenant_id,
                lab_id,
                overall,
                ppe_status,
                image_url,
                result,
                created_at
            ) VALUES (
                :entry_id,
                :tenant_id,
                :lab_id,
                :overall,
                :ppe_status,
                :image_url,
                :result,
                :created_at
            )
        """),
        {
            "entry_id": entry_id,
            "tenant_id": sdk["tenant_id"],
            "lab_id": lab_id,
            "overall": overall,
            "ppe_status": json.dumps(ppe_status),
            "image_url": image_url,
            "result": json.dumps(detection),
            "created_at": datetime.utcnow(),
        }
    )

    db.execute(
        text("""
            UPDATE sdk_commands
            SET status = 'DONE'
            WHERE entry_id = :entry_id
        """),
        {"entry_id": entry_id}
    )

    db.commit()   # ✅ DB FIRST (IMPORTANT)

    # -------------------------------
    # Upload to ATOMWALK (PRODUCTION DB)
    # -------------------------------
    temp_path = None
    try:
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        cv2.imwrite(temp_path, annotated)

        upload_ppe_result(
            image_path=temp_path,
            violation=overall,
            lab_id=lab_id
        )

    except Exception as e:
        print("⚠️ Atomwalk upload failed:", e)

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "status": "OK",
        "entry_id": entry_id,
        "overall": overall,
        "ppe_status": ppe_status,
        "image_url": image_url
    }
