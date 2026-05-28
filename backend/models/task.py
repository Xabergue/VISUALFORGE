# -*- coding: utf-8 -*-
"""
Modelo de Task — representa uma tarefa de geração de vídeo.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import Session

from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    style = Column(String, nullable=False)  # stock_footage | image_carousel | reddit_story | talking_head
    subject = Column(String, nullable=False)  # tema do vídeo
    config = Column(Text, nullable=True)  # JSON string com parâmetros do estilo
    status = Column(String, default="pending")  # pending | running | done | failed
    progress = Column(Integer, default=0)  # 0 a 100
    log = Column(Text, default="")  # logs concatenados em tempo real
    output_path = Column(String, nullable=True)  # caminho do vídeo gerado
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    def append_log(self, message: str, db: Session):
        """Adiciona uma mensagem ao log e salva no banco."""
        self.log = (self.log or "") + message + "\n"
        self.updated_at = utcnow()
        db.commit()
        db.refresh(self)

    def update_progress(self, progress: int, message: str, db: Session):
        """Atualiza o progresso e adiciona mensagem ao log."""
        self.progress = progress
        self.append_log(message, db)
