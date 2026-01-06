from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from app.db.session import Base

class EntryResult(Base):
    __tablename__ = "entry_results"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String, unique=True, index=True)

    user_id = Column(String, index=True)
    lab_id = Column(String, index=True)

    violation = Column(String)        # "OK" or "PPE_MISSING"
    snapshot_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="staff")
    created_at = Column(DateTime, default=datetime.utcnow)


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True)
    lab_id = Column(String, unique=True, index=True)


class EntryLog(Base):
    __tablename__ = "entry_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    lab_id = Column(String)
    compliant = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SDKCommand(Base):
    __tablename__ = "sdk_commands"

    id = Column(Integer, primary_key=True)
    sdk_id = Column(String, index=True)
    lab_id = Column(String, index=True)

    command = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING | SENT | DONE | FAILED

    payload = Column(String)  # JSON
    result = Column(String)   # JSON

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class SDKKey(Base):
    __tablename__ = "sdk_keys"

    id = Column(Integer, primary_key=True, index=True)
    sdk_id = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

