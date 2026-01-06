from fastapi import APIRouter, HTTPException
from app.db.session import SessionLocal
from app.db.models import User
from app.auth.security import hash_password

router = APIRouter()

@router.post("/register")
def register(user_id: str, email: str, password: str):
    db = SessionLocal()

    if db.query(User).filter(User.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        user_id=user_id,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}
