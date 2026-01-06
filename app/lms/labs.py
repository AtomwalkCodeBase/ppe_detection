from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Lab
from app.auth.dependencies import get_current_user
from app.lms.qr import generate_lab_qr

router = APIRouter()

@router.get("/labs/{lab_id}/qr")
def get_lab_qr(
    lab_id: str,
    current_user: str = Depends(get_current_user)
):
    db: Session = SessionLocal()

    lab = db.query(Lab).filter(Lab.lab_id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    return generate_lab_qr(lab_id)
