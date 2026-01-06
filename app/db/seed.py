from app.db.session import SessionLocal
from app.db.models import User, Lab
from app.auth.security import hash_password

db = SessionLocal()

user = db.query(User).filter(User.user_id == "E-1001").first()
if not user:
    user = User(
        user_id="E-1001",
        email="e1001@test.com",
        password_hash=hash_password("test123"),
        role="staff"
    )
    db.add(user)
    print("User seeded")
else:
    print("User already exists")

lab = db.query(Lab).filter(Lab.lab_id == "LAB-01").first()
if not lab:
    lab = Lab(
        lab_id="LAB-01"
    )
    db.add(lab)
    print("Lab seeded")
else:
    print("Lab already exists")

db.commit()
db.close()
