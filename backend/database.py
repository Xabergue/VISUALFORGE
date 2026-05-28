# -*- coding: utf-8 -*-
"""
Conexão com banco de dados SQLite via SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./visualforge.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessário para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency que fornece uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
