import os
from fastapi import Depends, Header, HTTPException, status

# ============================
# AUTH MODE
# ============================
# POC  -> no SSO, mocked user
# SSO  -> LMS injects identity
AUTH_MODE = os.getenv("AUTH_MODE", "POC")


def get_current_user(
    x_user_id: str = Header(None),
    x_user_email: str = Header(None)
):
    # ============================
    # POC MODE (NO SSO)
    # ============================
    if AUTH_MODE == "POC":
        return {
            "user_id": "POC-USER-001",
            "email": "poc.user@demo.com"
        }

    # ============================
    # REAL LMS SSO MODE
    # ============================
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing SSO identity"
        )

    return {
        "user_id": x_user_id,
        "email": x_user_email
    }
