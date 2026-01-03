from fastapi import Header, HTTPException, Depends
from app.db.session import SessionLocal
from app.db.models import SDKKey

def verify_sdk_key(x_api_key: str = Header(...)):
    db = SessionLocal()
    sdk = (
        db.query(SDKKey)
        .filter(SDKKey.api_key == x_api_key, SDKKey.active == 1)
        .first()
    )
    db.close()

    if not sdk:
        raise HTTPException(status_code=401, detail="Invalid SDK key")

    return {
        "sdk_id": sdk.sdk_id
    }
