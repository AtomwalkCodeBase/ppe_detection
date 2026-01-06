from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.utils.s3_signed_url import generate_signed_url

router = APIRouter()

@router.get("/entry-result/{entry_id}")
def entry_result(
    entry_id: str,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    tenant_id = user["tenant_id"]

    row = db.execute(
        text("""
            SELECT
                entry_id,
                lab_id,
                overall,
                ppe_status,
                image_url,
                created_at
            FROM entry_results
            WHERE entry_id = :entry_id
              AND tenant_id = :tenant_id
        """),
        {
            "entry_id": entry_id,
            "tenant_id": tenant_id
        }
    ).fetchone()

    # 🔴 KEY FIX: NO RESULT UNTIL IMAGE EXISTS
    if not row or not row.image_url:
        return {"status": "PROCESSING"}

    # image url handling
    if row.image_url.startswith("http"):
        image_url = row.image_url
    else:
        image_url = generate_signed_url(row.image_url)

    created_at = (
        row.created_at
        if isinstance(row.created_at, str)
        else row.created_at.isoformat()
    )

    return {
        "status": "DONE",
        "entry_id": row.entry_id,
        "lab_id": row.lab_id,
        "overall": row.overall,
        "ppe_status": row.ppe_status,
        "image_url": image_url,
        "created_at": created_at
    }
