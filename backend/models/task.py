import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime
from database import Base

def _utcnow():
    return datetime.now(timezone.utc)

def _new_id():
    return str(uuid.uuid4())

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=_new_id)
    style = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    config = Column(Text, default="{}")
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    log = Column(Text, default="")
    output_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
