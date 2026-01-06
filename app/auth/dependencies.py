import os
from fastapi import Header, HTTPException, status

# ============================
# AUTH MODE
# ============================
# POC  -> no SSO, mocked user
# SSO  -> LMS injects identity
AUTH_MODE = os.getenv("AUTH_MODE", "POC")

# ============================
# DEFAULT POC TENANT
# ============================
POC_TENANT_ID = os.getenv("POC_TENANT_ID", "TENANT-UNI-001")


def get_current_user(
    x_user_id: str = Header(None),
    x_user_email: str = Header(None),
    x_tenant_id: str = Header(None),
):
    # ============================
    # POC MODE (NO SSO)
    # ============================
    if AUTH_MODE == "POC":
        return {
            "user_id": "POC-USER-001",
            "email": "poc.user@demo.com",
            "tenant_id": POC_TENANT_ID
        }

    # ============================
    # REAL LMS SSO MODE
    # ============================
    if not x_user_id or not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing SSO identity or tenant"
        )

    return {
        "user_id": x_user_id,
        "email": x_user_email,
        "tenant_id": x_tenant_id
    }
